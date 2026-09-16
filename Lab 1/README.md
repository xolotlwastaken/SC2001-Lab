# SC2001 Lab 1 — Merge Sort + Insertion Sort

This project implements the hybrid algorithm, measures comparisons and CPU time, generates graphs, and provides an eight-minute presentation blueprint. Requirements come from `Project 1.pdf` and `info.pdf`; the rubric allocates 40% to correctness, 40% to analysis, and 20% to presentation.

## Start here

The finished presentation is `slides/SC2001_Project_1.pptx`, with a matching PDF. It includes eight main slides, seven backup slides, and speaker notes in the PowerPoint file.

1. Read `slides/blueprint.md` for the presentation and mathematical explanation.
2. Read `results/full/findings.md` for actual measured conclusions.
3. Use the six PNG/PDF graph pairs in `figures/`.
4. Run `java -cp build Demo` to demonstrate the algorithms on eight integers.
5. Read `JAVA_IMPLEMENTATION_GUIDE.md` for a plain-language explanation and run instructions.

The full-size evidence is in `results/full`. `results/smoke` and `figures/smoke` are pipeline checks and must not be presented as the required lab experiments.

## Build and test

From this directory, using Java 17 and Python 3:

```sh
make all
make test
make sanitize
java -cp build Demo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

`make all` compiles the Java sources and `make test` runs the Java correctness suite. `make sanitize` is retained as a compatibility target and reruns that suite because this project does not configure a Java memory sanitizer. The original C++ implementation can still be built with `make cpp-all`, `make cpp-test`, and `make cpp-sanitize`.

## Run the experiments

```sh
# Quick end-to-end check (different output directory).
.venv/bin/python scripts/run_experiments.py --smoke --output results/smoke --cpu-label 'Apple M5'
.venv/bin/python scripts/plot_results.py --results results/smoke --output figures/smoke

# Full assignment: includes 10 million elements and all five seeds.
.venv/bin/python scripts/run_experiments.py --cpu-label 'Apple M5'
.venv/bin/python scripts/plot_results.py
.venv/bin/python scripts/audit_results.py
```

Use your verified CPU name when rerunning on another machine. The original run used Apple M5. Close CPU-intensive applications and keep power conditions consistent. Runtime depends on the machine and the selected refinement interval; allow several minutes or longer. Do not run multiple benchmark processes concurrently.

Each completed size/seed/configuration batch is saved atomically under `results/full/shards/`. Running the same command resumes from complete batches. Changed build/source/configuration fingerprints require a fresh directory, for example `--output results/repeat-01`. This prevents silently mixing different implementations. Resumed batches can still experience different machine conditions; use a fresh uninterrupted run for a new final presentation dataset.

No plots rerun sorting. `plot_results.py` creates:

| File | Assignment part |
|---|---|
| `01_fixed_s` | (c)(i): comparisons against n, plus normalized counts |
| `02_fixed_n` | (c)(ii): comparisons against S at n=100,000 |
| `03_threshold_cpu` | (c)(iii): CPU time against S at four sizes |
| `04_threshold_comparisons` | (c)(iii): comparisons per element at four sizes |
| `05_refinement` | (c)(iii): detailed threshold tuning at 10 million |
| `06_validation` | (d): original versus hybrid on fresh 10-million-element arrays |

It also creates `summary.csv`, `validation_summary.csv`, and `findings.md` beside the measurements.

## Implementation map

- `src/Sorting.java`: stable algorithms and the counting/uncounted comparison policies.
- `src/MersenneTwister.java`: deterministic MT19937 generator used by the Java benchmark and tests.
- `src/Benchmark.java`: deterministic data, warm-ups, isolated timers, randomized run order, exact validation.
- `src/Tests.java`: edge cases, hand counts, randomized tests, and S=1 equivalence.
- `src/Demo.java`: quick presentation demonstration.
- `JAVA_IMPLEMENTATION_GUIDE.md`: plain-language implementation and run guide.
- `src/sorting.hpp`, `src/benchmark.cpp`, `src/tests.cpp`, and `src/demo.cpp`: retained C++ reference implementation.
- `scripts/run_experiments.py`: experimental design, checkpointing, threshold selection, held-out validation.
- `scripts/plot_results.py`: within-seed medians, across-seed summaries, graphs and findings.

The public wrapper is `Sorting.sortValues(values, auxiliary, hybrid, threshold, countComparisons)`. Allocate the auxiliary array to at least the input length before calling it. Threshold must be positive. `countComparisons=true` returns a 64-bit key-comparison count; `false` returns zero without incrementing a counter. Input keys are signed 32-bit integers. All recursive intervals are `[left, right)`.

The benchmark CLI is `java -cp build Benchmark N SEED REPS S_LIST ORDER_SEED`. In that CLI only, `0` in the comma-separated configuration list selects original merge sort; it is not a valid hybrid threshold. For example:

```sh
java -cp build Benchmark 1000 101 3 0,1,16,32 771
```

## What exactly is measured?

**Key comparisons:** only `leftKey <= rightKey` during merge and `previousKey > savedKey` during insertion. A final false key comparison counts. An index test that prevents evaluating a key comparison does not count. Copying remaining elements after a merge side is exhausted makes no key comparisons.

**CPU time:** Java `ThreadMXBean` current-thread CPU-time difference in seconds. **Elapsed time:** `System.nanoTime()` difference. Timed code includes the sort's function calls and recursion. It excludes array allocation, input generation, input copying, warm-up, reference sorting, validation, and CSV output. The elapsed interval surrounds the CPU timer reads, adding a tiny fixed overhead. Very short sorts are sensitive to timer resolution.

Each configuration gets a full-size unrecorded warm-up. Counted runs are separate. Three uncounted repetitions per seed are shuffled across configurations. Each candidate receives identical source data for a size/seed pair and uses a reusable auxiliary array. Exact equality with `Arrays.sort` output is checked after every sort. Stability follows from strict-greater insertion and left-first merge ties; tests compare integer values rather than tagged equal-key identities.

The Java benchmark uses the bundled `MersenneTwister` MT19937 implementation with rejection sampling, then `1 + value % 10,000,000`. It rejects values outside the largest multiple of 10,000,000 below 2³², avoiding modulo bias.

## Experimental design and statistics

- Sizes: 1k, 3k, 10k, 30k, 100k, 300k, 1m, 3m, 10m.
- Fixed threshold: 32.
- Coarse sweep: 1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128.
- Sweep sizes: 10k, 100k, 1m, 10m. The 100k subset supplies part (c)(ii).
- Tuning seeds: 101, 202, 303, 404, 505.
- Validation seeds: 1101, 1202, 1303, 1404, 1505.
- Three timed repetitions and one comparison-count pass per configuration/seed.

First take the median of three repetitions for each seed. Then take the median and 25th/75th percentiles across five seed summaries. The shaded IQR is not a confidence interval. Comparison counts have one deterministic observation per seed. Held-out speedup is calculated per seed as original CPU median / hybrid CPU median, then summarized across seeds; it is not necessarily equal to the ratio of overall medians.

Choose the coarse CPU winner at 10m, search every integer between its neighboring coarse thresholds, and reuse observations already recorded at coarse thresholds. Consider all measured candidates, minimizing the median-of-medians; smaller S breaks exact ties. Write `selection.json` before validation. Never retune from held-out results.

Integer thresholds may produce identical recursion partitions. At 10m, for example, a level can contain leaves of length 19 or 20; several S values can therefore perform identical work. Timing differences within such a plateau do not establish algorithmic superiority. The search yields the best observed candidate, not a proven optimum over all possible thresholds. Coarse and refinement phases happen at different times, so machine drift remains a limitation.

## CSV schema

`experiment, algorithm, n, threshold, seed, repetition, key_comparisons, cpu_seconds, elapsed_seconds, correct`

- `experiment`: `fixed_s`, `coarse`, `refine`, or `validation`.
- `algorithm`: `merge` or `hybrid`; threshold 0 labels merge only.
- Repetition 0 is a counted pass, with timing fields blank.
- Repetitions 1–3 are timed passes, with comparison counts blank.
- `correct=true` means exact equality with the sorted reference. A mismatch aborts the batch; no successful checkpoint is written.

Missing values mean “not measured in this pass,” not zero. Metadata records source/class fingerprints, seeds, generator, platform, CPU, Java runtime, and compiler flags. Reproducible data does not imply bit-identical timings.

## Presentation readiness

No submission is required for Projects 1 and 2 according to the supplied information sheet, but have source, graphs, and slides available locally. All practical work should be finished before the lab. The slot is 10 minutes including 2 minutes of Q&A; all teammates need to understand every section. Consult the supplied course instructions for attendance and team rules.

The original merge sort follows conventional lecture-style top-down merge sort; no lecture pseudocode was supplied for a line-by-line comparison. Optional alternative input distributions were not included in the required benchmark run.
