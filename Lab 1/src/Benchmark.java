import java.lang.management.ManagementFactory;
import java.lang.management.ThreadMXBean;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/**
 * Benchmark CLI.
 *
 * <p>Usage: Benchmark N SEED REPETITIONS THRESHOLDS ORDER_SEED</p>
 *
 * <p>THRESHOLDS is comma-separated; zero selects original merge sort.</p>
 */
public final class Benchmark {
    private static final long VALUE_RANGE = 10_000_000L;
    private static final long REJECTION_LIMIT =
            (1L << 32) / VALUE_RANGE * VALUE_RANGE;

    private Benchmark() {
    }

    public static void main(String[] args) {
        try {
            run(args);
        } catch (IllegalArgumentException | IllegalStateException exception) {
            System.err.println(exception.getMessage());
            System.exit(1);
        }
    }

    private static void run(String[] args) {
        if (args.length != 5) {
            throw new IllegalArgumentException(
                    "Usage: Benchmark N SEED REPS S_LIST ORDER_SEED");
        }

        int n = parsePositiveInt(args[0], "N");
        long seed = parseUnsignedSeed(args[1], "SEED");
        int repetitions = parsePositiveInt(args[2], "REPS");
        if (n > 10_000_000) {
            throw new IllegalArgumentException("N must be 1..10000000 and REPS positive");
        }
        List<Integer> thresholds = parseThresholds(args[3]);
        long orderSeed = parseUnsignedSeed(args[4], "ORDER_SEED");

        MersenneTwister valueRng = new MersenneTwister(seed);
        MersenneTwister orderRng = new MersenneTwister(orderSeed);
        int[] source = new int[n];
        int[] expected;
        int[] values = new int[n];
        int[] buffer = new int[n];

        for (int i = 0; i < source.length; i++) {
            long value;
            do {
                value = valueRng.nextUInt32();
            } while (value >= REJECTION_LIMIT);
            source[i] = (int) (1 + value % VALUE_RANGE);
        }

        expected = source.clone();
        Arrays.sort(expected);

        shuffle(thresholds, orderRng);
        for (int threshold : thresholds) {
            values = source.clone();
            sortConfiguration(values, buffer, threshold, false);
            requireCorrect(values, expected, "warm-up validation failed");
        }

        for (int threshold : thresholds) {
            values = source.clone();
            long count = sortConfiguration(values, buffer, threshold, true);
            requireCorrect(values, expected, "count validation failed");
            printCountRow(n, threshold, seed, count);
        }

        List<Job> jobs = new ArrayList<>(repetitions * thresholds.size());
        for (int repetition = 1; repetition <= repetitions; repetition++) {
            for (int threshold : thresholds) {
                jobs.add(new Job(threshold, repetition));
            }
        }
        shuffle(jobs, orderRng);

        CpuTimer cpuTimer = new CpuTimer();
        for (Job job : jobs) {
            values = source.clone();
            long wallStart = System.nanoTime();
            long cpuStart = cpuTimer.read();
            sortConfiguration(values, buffer, job.threshold(), false);
            long cpuEnd = cpuTimer.read();
            long wallEnd = System.nanoTime();
            requireCorrect(values, expected, "timed validation failed");

            double cpuSeconds = (cpuEnd - cpuStart) / 1_000_000_000.0;
            double elapsedSeconds = (wallEnd - wallStart) / 1_000_000_000.0;
            printTimedRow(n, job.threshold(), seed, job.repetition(),
                    cpuSeconds, elapsedSeconds);
        }
    }

    private static int parsePositiveInt(String value, String name) {
        try {
            int parsed = Integer.parseInt(value);
            if (parsed < 1) {
                throw new IllegalArgumentException(name + " must be positive");
            }
            return parsed;
        } catch (NumberFormatException exception) {
            throw new IllegalArgumentException("invalid " + name + ": " + value);
        }
    }

    private static long parseUnsignedSeed(String value, String name) {
        try {
            return Long.parseUnsignedLong(value);
        } catch (NumberFormatException exception) {
            throw new IllegalArgumentException("invalid " + name + ": " + value);
        }
    }

    private static List<Integer> parseThresholds(String value) {
        if (value.isBlank()) {
            throw new IllegalArgumentException("empty threshold list");
        }

        String[] items = value.split(",", -1);
        List<Integer> thresholds = new ArrayList<>(items.length);
        for (String item : items) {
            try {
                int threshold = Integer.parseInt(item.trim());
                if (threshold < 0) {
                    throw new IllegalArgumentException("negative threshold");
                }
                thresholds.add(threshold);
            } catch (NumberFormatException exception) {
                throw new IllegalArgumentException("invalid threshold: " + item);
            }
        }
        if (thresholds.isEmpty()) {
            throw new IllegalArgumentException("empty threshold list");
        }
        return thresholds;
    }

    private static long sortConfiguration(
            int[] values,
            int[] buffer,
            int threshold,
            boolean countComparisons) {
        boolean hybrid = threshold != 0;
        int effectiveThreshold = hybrid ? threshold : 1;
        return Sorting.sortValues(
                values,
                buffer,
                hybrid,
                effectiveThreshold,
                countComparisons);
    }

    private static void requireCorrect(int[] values, int[] expected, String message) {
        if (!Arrays.equals(values, expected)) {
            throw new IllegalStateException(message);
        }
    }

    private static void printCountRow(int n, int threshold, long seed, long count) {
        System.out.printf(
                Locale.ROOT,
                "%s,%d,%d,%s,0,%d,,,true%n",
                threshold == 0 ? "merge" : "hybrid",
                n,
                threshold,
                Long.toUnsignedString(seed),
                count);
    }

    private static void printTimedRow(
            int n,
            int threshold,
            long seed,
            int repetition,
            double cpuSeconds,
            double elapsedSeconds) {
        System.out.printf(
                Locale.ROOT,
                "%s,%d,%d,%s,%d,,%.12g,%.12g,true%n",
                threshold == 0 ? "merge" : "hybrid",
                n,
                threshold,
                Long.toUnsignedString(seed),
                repetition,
                cpuSeconds,
                elapsedSeconds);
    }

    private static <T> void shuffle(List<T> values, MersenneTwister random) {
        for (int i = values.size() - 1; i > 0; i--) {
            int swapIndex = random.nextInt(i + 1);
            T temporary = values.get(i);
            values.set(i, values.get(swapIndex));
            values.set(swapIndex, temporary);
        }
    }

    private record Job(int threshold, int repetition) {
    }

    private static final class CpuTimer {
        private final ThreadMXBean bean;

        private CpuTimer() {
            bean = ManagementFactory.getThreadMXBean();
            if (!bean.isCurrentThreadCpuTimeSupported()) {
                throw new IllegalStateException("CPU clock unavailable");
            }
            try {
                if (!bean.isThreadCpuTimeEnabled()) {
                    bean.setThreadCpuTimeEnabled(true);
                }
            } catch (SecurityException | UnsupportedOperationException exception) {
                throw new IllegalStateException("CPU clock unavailable", exception);
            }
        }

        private long read() {
            long value = bean.getCurrentThreadCpuTime();
            if (value < 0) {
                throw new IllegalStateException("CPU clock unavailable");
            }
            return value;
        }
    }
}
