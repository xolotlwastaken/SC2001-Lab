# Measured slide content — full assignment run

These statements are generated from `results/full/measurements.csv`. Refer to the blueprint for speaker notes and timings.

## Slide 4: method footer

**Apple M5 · C++17 · clang++ -O3 · uniform integers [1, 10⁷] · five seeds × three repetitions.**

## Slide 5: result headline

**At S=32, comparison growth is consistent with n log₂n scaling over the tested sizes.**

The normalized ratio C/(n log₂n) ranges from **1.042 to 1.343**. This is empirical consistency, not a proof of the bound.

## Slide 6: result callout

**Selected S=64 after coarse search and integer refinement at 10 million elements.**

Coarse winners: {'10000': 48, '100000': 96, '1000000': 32, '10000000': 64}. Refined interval: [48, 96]. Candidates within 1% of the best median: [32, 48, 64]. Describe this as a measured fast region; do not claim each tiny timing difference is meaningful.

The comparison-count winner at 10 million is **S=1**, while the CPU-time winner is **S=64**. Candidates with identical observed comparison counts to the selected threshold: [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75].

The refinement graph distinguishes reused coarse observations from later measurements. Their timing differences within the same leaf partition show why the exact rank is not established robustly. The held-out hybrid-versus-original comparison supports the final speedup claim.

## Slide 7: result headline

**Hybrid S=64: 1.147× paired median speedup; +27.8% key comparisons on fresh data.**

| Measurement | Original merge | Hybrid |
|---|---:|---:|
| Median CPU seconds | 0.443770 | 0.386277 |
| CPU IQR | 0.443461–0.443864 | 0.385783–0.389874 |
| Median key comparisons | 220,101,526 | 281,233,315 |

Paired speedup IQR: **1.138–1.152×**. Speedup above 1 favors hybrid; below 1 favors original merge.

## Slide 8: three conclusions

1. Correctness: optimized and sanitizer checks passed; every recorded sort matched its reference.
2. Complexity: fixed-S measurements are consistent with the derived n log n growth; threshold changes affect both leaf work and merge levels.
3. Performance: on this machine and distribution, the selected hybrid achieved **1.147×** paired median speedup with **+27.8%** comparisons.

**Limitation:** this is a measured threshold for one implementation and environment, with five held-out datasets; it is not a universal optimum.
