public final class Demo {
    private Demo() {
    }

    public static void main(String[] args) {
        int[] input = {7, 2, 5, 1, 6, 3, 4, 2};
        int[] buffer = new int[input.length];

        System.out.print("Input:  ");
        printValues(input);
        System.out.println("Hybrid S=4: two insertion-sort leaves of length 4, then merge.");

        int[] thresholds = {0, 1, 4, 8};
        for (int threshold : thresholds) {
            int effectiveThreshold = threshold == 0 ? 1 : threshold;
            int[] values = input.clone();
            long count = Sorting.sortValues(
                    values,
                    buffer,
                    threshold != 0,
                    effectiveThreshold,
                    true);
            System.out.print((threshold == 0 ? "Merge " : "Hybrid")
                    + " S=" + threshold + ": ");
            printValues(values);
            System.out.println(" | key comparisons=" + count);
        }
    }

    private static void printValues(int[] values) {
        for (int value : values) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}
