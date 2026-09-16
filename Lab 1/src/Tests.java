import java.util.Arrays;

public final class Tests {
    private Tests() {
    }

    public static void main(String[] args) {
        try {
            runAll();
            System.out.println(
                    "PASS: edge cases, threshold boundaries, randomized arrays, "
                            + "counting, S=1 equivalence");
        } catch (AssertionError exception) {
            System.err.println(exception.getMessage());
            System.exit(1);
        }
    }

    private static void runAll() {
        int[][] fixedInputs = {
                {},
                {1},
                {2, 1},
                {1, 2, 3},
                {3, 2, 1},
                {1, 1, 1, 1},
                {3, 1, 3, 2, 1},
                {-3, 0, Integer.MAX_VALUE, Integer.MIN_VALUE}
        };
        for (int[] input : fixedInputs) {
            check(input);
        }

        MersenneTwister random = new MersenneTwister(8128);
        for (int n = 0; n <= 260; n++) {
            int[] values = new int[n];
            for (int trial = 0; trial < 8; trial++) {
                for (int i = 0; i < values.length; i++) {
                    values[i] = (int) (random.nextUInt32() % 31) - 15;
                }
                check(values);
            }
            Arrays.sort(values);
            check(values);
            reverse(values);
            check(values);
        }

        CountCase[] hybridCases = {
                new CountCase(new int[]{}, 0),
                new CountCase(new int[]{1}, 0),
                new CountCase(new int[]{1, 2, 3, 4}, 3),
                new CountCase(new int[]{4, 3, 2, 1}, 6),
                new CountCase(new int[]{2, 1, 3}, 2),
                new CountCase(new int[]{1, 1, 1, 1}, 3),
                new CountCase(new int[]{3, 1, 2}, 3)
        };
        for (CountCase test : hybridCases) {
            int[] values = test.values().clone();
            int[] buffer = new int[values.length];
            require(
                    Sorting.sortValues(values, buffer, true, 128, true)
                            == test.expectedComparisons(),
                    "hand count mismatch");
        }

        CountCase[] mergeCases = {
                new CountCase(new int[]{2, 1}, 1),
                new CountCase(new int[]{2, 4, 1, 3}, 5),
                new CountCase(new int[]{1, 2, 3, 4}, 4)
        };
        for (CountCase test : mergeCases) {
            int[] values = test.values().clone();
            int[] buffer = new int[values.length];
            require(
                    Sorting.sortValues(values, buffer, false, 1, true)
                            == test.expectedComparisons(),
                    "merge hand count mismatch");
        }

        boolean rejected = false;
        try {
            Sorting.sortValues(new int[]{1}, new int[]{1}, true, 0, true);
        } catch (IllegalArgumentException exception) {
            rejected = true;
        }
        require(rejected, "S=0 accepted");

        rejected = false;
        try {
            Sorting.sortValues(new int[]{1}, new int[0], false, 1, true);
        } catch (IllegalArgumentException exception) {
            rejected = true;
        }
        require(rejected, "short buffer accepted");
    }

    private static void check(int[] input) {
        int[] expected = input.clone();
        Arrays.sort(expected);
        int[] buffer = new int[input.length];

        int[] ordinary = input.clone();
        long baseline = Sorting.sortValues(ordinary, buffer, false, 1, true);
        require(Arrays.equals(ordinary, expected), "merge sort mismatch");

        int[] thresholds = {1, 2, 3, 4, 8, 16, 32, 64, 128, 1024};
        for (int threshold : thresholds) {
            int[] values = input.clone();
            long comparisons = Sorting.sortValues(
                    values, buffer, true, threshold, true);
            require(Arrays.equals(values, expected), "hybrid mismatch");
            if (threshold == 1) {
                require(comparisons == baseline, "S=1 count mismatch");
            }

            values = input.clone();
            require(
                    Sorting.sortValues(values, buffer, true, threshold, false) == 0,
                    "timed policy counted");
            require(Arrays.equals(values, expected), "uncounted mismatch");
        }

        int[] values = input.clone();
        Sorting.sortValues(values, buffer, false, 1, false);
        require(Arrays.equals(values, expected), "uncounted merge mismatch");
    }

    private static void reverse(int[] values) {
        for (int left = 0, right = values.length - 1; left < right; left++, right--) {
            int temporary = values[left];
            values[left] = values[right];
            values[right] = temporary;
        }
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private record CountCase(int[] values, long expectedComparisons) {
    }
}
