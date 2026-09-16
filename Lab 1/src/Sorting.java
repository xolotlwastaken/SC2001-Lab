import java.util.Objects;

/**
 * Stable top-down merge sort and the hybrid merge/insertion sort used by the
 * SC2001 experiments.
 */
public final class Sorting {
    private Sorting() {
    }

    /**
     * Sorts {@code values} in ascending order.
     *
     * @param values input array, sorted in place
     * @param buffer reusable auxiliary array with length at least values.length
     * @param hybrid whether to use insertion sort at small recursive leaves
     * @param threshold positive insertion-sort leaf threshold
     * @param countComparisons whether key comparisons should be counted
     * @return the number of key comparisons, or zero when counting is disabled
     */
    public static long sortValues(
            int[] values,
            int[] buffer,
            boolean hybrid,
            int threshold,
            boolean countComparisons) {
        Objects.requireNonNull(values, "values");
        Objects.requireNonNull(buffer, "buffer");
        if (threshold < 1) {
            throw new IllegalArgumentException("S must be at least 1");
        }
        if (buffer.length < values.length) {
            throw new IllegalArgumentException("buffer too small");
        }

        KeyOrder order = countComparisons
                ? new CountingKeyOrder()
                : new UncountedKeyOrder();
        if (hybrid) {
            hybridSort(values, buffer, 0, values.length, threshold, order);
        } else {
            mergeSort(values, buffer, 0, values.length, order);
        }
        return order.comparisons();
    }

    private interface KeyOrder {
        boolean lessEqual(int left, int right);

        boolean greater(int left, int right);

        long comparisons();
    }

    private static final class CountingKeyOrder implements KeyOrder {
        private long comparisonCount;

        @Override
        public boolean lessEqual(int left, int right) {
            comparisonCount++;
            return left <= right;
        }

        @Override
        public boolean greater(int left, int right) {
            comparisonCount++;
            return left > right;
        }

        @Override
        public long comparisons() {
            return comparisonCount;
        }
    }

    private static final class UncountedKeyOrder implements KeyOrder {
        @Override
        public boolean lessEqual(int left, int right) {
            return left <= right;
        }

        @Override
        public boolean greater(int left, int right) {
            return left > right;
        }

        @Override
        public long comparisons() {
            return 0;
        }
    }

    private static void insertionSort(
            int[] values,
            int left,
            int right,
            KeyOrder order) {
        for (int i = left + 1; i < right; i++) {
            int key = values[i];
            int j = i;
            while (j > left && order.greater(values[j - 1], key)) {
                values[j] = values[j - 1];
                j--;
            }
            values[j] = key;
        }
    }

    private static void merge(
            int[] values,
            int[] buffer,
            int left,
            int mid,
            int right,
            KeyOrder order) {
        int i = left;
        int j = mid;
        int k = left;
        while (i < mid && j < right) {
            if (order.lessEqual(values[i], values[j])) {
                buffer[k++] = values[i++];
            } else {
                buffer[k++] = values[j++];
            }
        }
        while (i < mid) {
            buffer[k++] = values[i++];
        }
        while (j < right) {
            buffer[k++] = values[j++];
        }
        for (k = left; k < right; k++) {
            values[k] = buffer[k];
        }
    }

    private static void hybridSort(
            int[] values,
            int[] buffer,
            int left,
            int right,
            int threshold,
            KeyOrder order) {
        if (right - left <= 1) {
            return;
        }
        if (right - left <= threshold) {
            insertionSort(values, left, right, order);
            return;
        }
        int mid = left + (right - left) / 2;
        hybridSort(values, buffer, left, mid, threshold, order);
        hybridSort(values, buffer, mid, right, threshold, order);
        merge(values, buffer, left, mid, right, order);
    }

    private static void mergeSort(
            int[] values,
            int[] buffer,
            int left,
            int right,
            KeyOrder order) {
        if (right - left <= 1) {
            return;
        }
        int mid = left + (right - left) / 2;
        mergeSort(values, buffer, left, mid, order);
        mergeSort(values, buffer, mid, right, order);
        merge(values, buffer, left, mid, right, order);
    }
}
