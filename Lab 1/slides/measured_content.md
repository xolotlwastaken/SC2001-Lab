# Measured slide content — full assignment run

These statements are generated from the selected full-run `measurements.csv`. Refer to the blueprint for speaker notes and timings.

## Slide 4: method footer

**Apple M5 · openjdk version "26.0.2.1" 2026-08-18 · javac --release 17 · uniform integers [1, 10⁷] · five seeds × 5 repetitions.**

## Slide 5: result headline

**At S=32, comparison growth is consistent with n log₂n scaling over the tested sizes.**

The normalized ratio C/(n log₂n) ranges from **1.042 to 1.343**. This is empirical consistency, not a proof of the bound.

## Slide 6: result callout

**Selected S=192 after coarse search and partition-aware refinement at 10 million elements.**

Coarse winners: {'10000': 192, '100000': 192, '1000000': 96, '10000000': 256}. Refined interval: [192, 384], with distinct-partition representatives [192, 305, 306]. Candidates within 1% of the best median: [192]. Describe this as a measured fast region; do not claim each tiny timing difference is meaningful.

The comparison-count winner at 10 million is **S=1**, while the CPU-time winner is **S=192**. Candidates with identical observed comparison counts to the selected threshold: [192, 256].

The refinement phase retests comparable structural candidates together and avoids ranking thresholds that produce identical recursion leaves. The held-out hybrid-versus-original comparison supports the final speedup claim.

## Slide 7: result headline

**Hybrid S=192: 1.293× paired median speedup; +149.2% key comparisons on fresh data.**

| Measurement | Original merge | Hybrid |
|---|---:|---:|
| Median CPU seconds | 0.841846 | 0.655154 |
| CPU IQR | 0.841275–0.850693 | 0.651119–0.746257 |
| Median key comparisons | 220,101,526 | 548,538,181 |

Paired speedup IQR: **1.126–1.294×**. Speedup above 1 favors hybrid; below 1 favors original merge.

## Slide 8: three conclusions

1. Correctness: the Java correctness suite passed; every recorded sort matched its reference.
2. Complexity: fixed-S measurements are consistent with the derived n log n growth; threshold changes affect both leaf work and merge levels.
3. Performance: on this machine and distribution, the selected hybrid achieved **1.293×** paired median speedup with **+149.2%** comparisons.

**Limitation:** this is a measured threshold for one implementation and environment, with five held-out datasets; it is not a universal optimum.
