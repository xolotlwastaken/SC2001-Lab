# Java Implementation Guide

This guide explains the Java version of the SC2001 sorting project. It describes the algorithm, the random test data, the demo, the correctness tests, and the commands needed to run everything.

## Requirements

Install a Java 17 JDK. A JDK is required because the project must compile the source files with `javac`.

Check the installation from the project directory:

```sh
java -version
javac -version
```

The project uses the default Java package, so no additional libraries or project framework are required.

## Java files

### Sorting.java

`Sorting.java` contains both sorting algorithms:

- Ordinary top-down merge sort.
- A hybrid sort that uses insertion sort when a recursive subarray has at most `S` elements.

The input is an `int[]` array and is sorted in place. A second `int[]` array is supplied as reusable merge-sort workspace. The method checks that `S` is positive and that the workspace is large enough.

The public method is:

```java
Sorting.sortValues(values, buffer, hybrid, threshold, countComparisons)
```

When `countComparisons` is `true`, the method returns the number of key comparisons. When it is `false`, it returns zero and uses an uncounted comparison policy for timed runs. Only these comparisons are counted:

- `leftValue <= rightValue` during merging.
- `previousValue > savedValue` during insertion sort.

The merge is stable because equal values are taken from the left half first. Insertion sort is stable because it moves only strictly larger values.

### MersenneTwister.java

`MersenneTwister.java` is a small implementation of the MT19937 random-number generator. It produces the same 32-bit sequence as C++ `std::mt19937` when given the same seed.

It is not a sorting algorithm. It is used so that the random arrays in the tests and benchmark are repeatable. The benchmark also uses it to shuffle the order in which threshold configurations are run.

For benchmark values, generated numbers are in the range 1 to 10,000,000. Rejection sampling is used before taking the remainder, which avoids modulo bias.

### Benchmark.java

`Benchmark.java` runs the performance experiments. It:

1. Generates one deterministic random input array.
2. Creates a sorted reference using `Arrays.sort`.
3. Runs an uncounted warm-up for every threshold.
4. Runs one counted pass for every threshold.
5. Runs the requested timed repetitions.
6. Checks every result against the sorted reference.
7. Prints CSV rows containing the algorithm, input size, threshold, seed, repetition, comparison count, CPU time, elapsed time, and correctness.

The benchmark uses the current-thread CPU timer from `ThreadMXBean` and `System.nanoTime()` for elapsed time.

A threshold of `0` means ordinary merge sort. A positive threshold means hybrid sort.

### Demo.java

`Demo.java` is a small example that sorts:

```text
7 2 5 1 6 3 4 2
```

It displays the sorted output and comparison count for ordinary merge sort and hybrid thresholds `S=1`, `S=4`, and `S=8`. It is intended for a quick visual demonstration, not for performance measurement.

### Tests.java

`Tests.java` is a standalone correctness test program. It does not require JUnit.

It checks:

- Empty and one-element arrays.
- Sorted, reverse-sorted, duplicate, and mixed-value arrays.
- Negative values and integer minimum and maximum values.
- Random arrays for every size from 0 through 260, with eight random trials per size.
- Sorted and reverse-sorted versions of every tested size.
- Hybrid thresholds `1, 2, 3, 4, 8, 16, 32, 64, 128, 1024`.
- Hand-calculated comparison counts.
- The fact that `S=1` has the same comparison count as ordinary merge sort.
- The fact that uncounted runs return zero comparisons.
- Rejection of an invalid threshold and an undersized buffer.

There are 2,618 input-array checks in the main randomized and fixed-input suite.

## Experiment settings

### Threshold values

The full experiment uses a two-stage search for the insertion-sort threshold `S`.

- The coarse sweep tests 11 values: `1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128`.
- The coarse sweep is run at four input sizes: 10,000, 100,000, 1,000,000, and 10,000,000.
- The best coarse result at 10,000,000 elements was `S=64`. The neighboring coarse values were `48` and `96`.
- The refinement stage tests every integer from `48` through `96`.

This means 46 additional thresholds are tested during refinement, because `48`, `64`, and `96` were already part of the coarse sweep. The experiment therefore tests **57 unique hybrid S values overall**. Threshold `0` is only the label for the ordinary merge-sort baseline; it is not a hybrid threshold.

The values are chosen to cover a wide range without immediately timing every possible integer. `S=1` provides the ordinary merge-sort comparison baseline. Powers of two and intermediate values show how the threshold affects recursive leaf sizes, merge levels, and insertion-sort work. Once the coarse winner is known, testing every nearby integer gives a more detailed local result while keeping the experiment practical.

This is a search for the best measured threshold, not a proof that no better value exists outside the tested range.

### Seeds

The tuning stages use five seeds: `101, 202, 303, 404, 505`. These seeds are used for the fixed-threshold, coarse-sweep, and refinement measurements.

The final validation stage uses five different held-out seeds: `1101, 1202, 1303, 1404, 1505`. They are kept separate so the selected threshold is not chosen using the same data used to evaluate it. There are **10 distinct seeds in total**.

### Iterations for each seed

For every combination of input size, seed, and threshold, the benchmark performs:

1. One full-size warm-up sort. This is not recorded.
2. One comparison-count sort. This is recorded as repetition `0`.
3. Three timed sorts. These are recorded as repetitions `1`, `2`, and `3`.

Therefore, there are **3 timed iterations per seed and threshold**, plus one counted pass and one unrecorded warm-up. Each configuration produces four recorded CSV rows and performs five sorting executions in total.

The completed full experiment contains 505 configuration-and-seed groups and 2,020 recorded rows.

## Running with the Makefile

From the project directory, compile all Java files:

```sh
make all
```

Run the Java correctness tests:

```sh
make test
```

Run the demo:

```sh
java -cp build Demo
```

The `sanitize` target is kept for compatibility with the original project. It reruns the Java correctness tests because this project does not configure a Java equivalent of AddressSanitizer:

```sh
make sanitize
```

## Running without the Makefile

Create the build directory and compile the Java sources manually:

```sh
mkdir -p build
javac --release 17 -d build src/Sorting.java src/MersenneTwister.java src/Benchmark.java src/Demo.java src/Tests.java
```

Run the demo:

```sh
java -cp build Demo
```

Run the tests:

```sh
java -cp build Tests
```

The expected successful test message starts with:

```text
PASS: edge cases, threshold boundaries, randomized arrays, counting, S=1 equivalence
```

## Running the benchmark manually

The command format is:

```sh
java -cp build Benchmark N SEED REPS S_LIST ORDER_SEED
```

Example:

```sh
java -cp build Benchmark 1000 101 3 0,1,16,32 771
```

The example means:

- `N=1000`: generate 1,000 input values.
- `SEED=101`: use 101 for the input generator.
- `REPS=3`: perform three timed repetitions per configuration.
- `S_LIST=0,1,16,32`: test ordinary merge sort (`0`) and hybrid thresholds 1, 16, and 32.
- `ORDER_SEED=771`: use 771 to shuffle the run order.

The benchmark prints CSV rows to the terminal. The Python experiment script runs this same Java command automatically and saves the rows under the results directory.
