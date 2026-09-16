# Eight-minute presentation blueprint

Audience: SC2001 lab TA and classmates familiar with basic sorting. Use eight main slides and keep detailed tables in the appendix. Copy actual numbers from `results/full/findings.md` and `validation_summary.csv`; never substitute smoke-test results. The measured slide text is in `slides/measured_content.md` after the full run.

## Slide 1 — Can a small-array switch make merge sort faster? (0:00–0:30)

**On slide**

- Hybrid merge sort + insertion sort.
- n = input length; S = insertion-sort threshold.
- Question: which S minimizes CPU time, and does it also minimize comparisons?
- Team member names and lab group.

**Visual:** one simple pipeline: split → insertion-sort small leaves → merge.

**Say:** “Merge sort scales well, but recursive splitting and merging add overhead on small subarrays. We keep its structure and replace only the small-leaf work. We measure both key comparisons and CPU time because they need not favor the same threshold.”

**Transition:** “Here is the exact switch we implemented.”

## Slide 2 — Sort small leaves, then merge sorted halves (0:30–1:40)

**On slide:** the following pseudocode, with a recursion tree beside it.

```text
hybrid(A, left, right, S):
    if right-left <= 1: return
    if right-left <= S:
        insertionSort(A, left, right)
        return
    mid = left + (right-left)/2
    hybrid(A, left, mid, S)
    hybrid(A, mid, right, S)
    merge(A, left, mid, right)
```

**Tree:** n=16, S=4: one 16 node → two 8 nodes → four highlighted 4-element leaves. Label leaves “insertion sort,” upper levels “merge.”

**Footer:** stable; one reusable auxiliary array; tests against `std::sort`.

**Say:** “Intervals exclude the right endpoint. Insertion sort maintains a sorted prefix, so every leaf is sorted. By induction, recursive calls return sorted halves. Merge repeatedly selects the smaller front element, so the combined interval is sorted and preserves all elements. Insertion shifts only strictly larger values, and merge takes the left value on ties, preserving stability.”

**Code reference:** `src/sorting.hpp`. Show pseudocode rather than a screenshot of the whole source file.

## Slide 3 — Threshold trades insertion work for merge levels (1:40–2:40)

**On slide**

\[
\underbrace{O((n/S)S^2)}_{\text{small-leaf sorting}}+
\underbrace{O(n\log_2(n/S))}_{\text{merge levels}}
=O(nS+n\log_2(n/S)).
\]

- Fixed S: Θ(n log n) worst case.
- S=1: ordinary merge sort. S≥n: insertion sort.
- Auxiliary space: O(n), plus recursion stack.

**Say:** “Roughly n/S leaves each require at most quadratic insertion work in S. Each merge level processes at most n elements, and there are roughly log₂(n/S) levels. Increasing S reduces merge levels but increases insertion work. This is a worst-case growth bound, not an exact curve for random data and not a formula that directly tells us the fastest threshold.”

**Precision for questions:** for non-power-of-two sizes, leaves differ by at most one within a depth and can occur at adjacent depths; the asymptotic bound survives rounding. For n≥2 and 1≤S≤n, insertion leaf lengths are O(S). Fixed S gives the usual worst-case lower and upper order. For S≥n, cap the leaf size at n.

## Slide 4 — Fair inputs, isolated timing, fresh validation (2:40–3:30)

**On slide**

- Uniform integers in [1, 10⁷]; n from 10³ to 10⁷.
- Five tuning seeds; three timed repetitions per seed.
- Same inputs across candidates; shuffled configuration order and warm-up.
- Timers cover sorting only; counters compiled out of timed runs.
- Choose S first; compare on five fresh seeds.
- Machine/build: insert verified metadata from the measured content file.

**Say:** “A key comparison is a comparison of two data values, including a false comparison that terminates insertion. Index checks are excluded. We count in a separate pass. We summarize repetitions within each seed, then summarize across seeds. Bands are interquartile ranges, not confidence intervals. Every sort is checked against a reference outside the timer.”

## Slide 5 — Does comparison growth agree with theory? (3:30–4:25)

**Visual:** `figures/01_fixed_s.png` occupying most of the slide. Retain both panels.

**On slide:** “S=32, nine input sizes.” Add one measured sentence from `slides/measured_content.md` about the normalized range.

**Say:** “The left panel shows the growth of key comparisons on logarithmic axes. The dashed curve is n log₂n scaled to the largest data point, so it is a reference, not a theoretical prediction of the exact count. The right panel divides by n log₂n. A broadly stable ratio supports the fixed-threshold growth prediction. Finite-size changes and leaf work explain why the ratio need not be perfectly constant.”

**Avoid:** claiming that any straight log-log plot proves n log n, or asserting the fitted reference validates an exact formula.

## Slide 6 — Runtime and comparisons favor different tradeoffs (4:25–5:45)

**Visual layout:** left 40%: `02_fixed_n.png`; right 60%: `03_threshold_cpu.png`. Use a build/animation or two sequential reveals on the same slide if labels are too small. Put the detailed refinement graph in the appendix.

**On slide**

- Comparison sweep at n=100,000.
- CPU sweeps at four sizes; orange points mark coarse winners.
- Fine search at 10m → selected S from actual results.
- Several S values can create identical recursion leaves.

**Say:** “Fewer key comparisons do not necessarily mean less CPU time. Small insertion-sort leaves can avoid recursive calls and buffer copying even when they make more comparisons. The curves are stepped because the switch depends on actual recursive subarray sizes. We refine around the coarse winner at 10 million and freeze the measured winner before testing fresh seeds. Nearby thresholds with similar times should be described as a fast region rather than a sharply established universal optimum.”

Use a result-dependent headline after checking the actual curves; if the claimed tradeoff does not appear, replace the headline with “Measured effect of the threshold.”

## Slide 7 — Held-out comparison at ten million integers (5:45–6:45)

**Visual:** `figures/06_validation.png` full width.

**On slide:** exact selected S, original/hybrid CPU medians, paired speedup and comparison percentage change. Copy from `slides/measured_content.md`.

**Say:** “These seeds were not used to choose S. Both algorithms sort identical arrays. The speedup is original CPU time divided by hybrid CPU time, computed within each seed and then summarized. The error bars show the variation across seeds. Our conclusion is limited to this implementation, machine, and input distribution.”

If hybrid is slower, say so directly. Do not change S after seeing validation.

## Slide 8 — Demonstration and three conclusions (6:45–8:00)

**Demo, 35 seconds:** run `./build/demo` in an already-open terminal. Input `[7,2,5,1,6,3,4,2]`; sorted output `[1,2,2,3,4,5,6,7]`. Ordinary merge and hybrid S=1 both use 17 comparisons; S=4 uses 19; S=8 uses 22. Explain that tiny examples demonstrate behavior, not meaningful timing.

**On slide, 40 seconds**

1. Correctness: reference checks and sanitizer tests passed.
2. Analysis: fixed-S behavior agrees with the expected growth to the extent shown by data.
3. Performance: insert the actual held-out finding and chosen threshold.

**Limitation:** the best measured threshold is implementation/machine/data dependent; timing noise makes neighboring thresholds hard to rank.

**Reproducibility footer:** `make test`, `scripts/run_experiments.py`, `scripts/plot_results.py`. Show commands briefly; do not execute the full experiment during the presentation.

**Fallback:** if the terminal is unavailable, show the saved demo output in `slides/demo-output.txt`.

## Appendix A — Key-comparison examples

Insertion sorting `[2,1,3]` uses two comparisons: `2>1` true, then `2>3` false. Reaching the left boundary after shifting 2 does not compare another pair of keys. Sorted `[1,2,3,4]` uses 3 comparisons; reversed `[4,3,2,1]` uses 6. Equal `[1,1,1,1]` uses 3 and remains stable.

Merging `[1,3]` and `[2,4]` uses three key comparisons: 1≤2, 3≤2, 3≤4. Copying the remaining 4 needs no key comparison.

## Appendix B — Derivation and special cases

For distinct randomly ordered keys in a leaf of length m, expected inversions are m(m−1)/4. Insertion sort shifts once per inversion and performs up to m−1 additional terminating key comparisons. This explains its quadratic expected leaf cost for random distinct keys. Our generated arrays can contain ties, so treat this as intuition, not an exact expected-count formula for this dataset.

For S=1, worst-case merge comparisons obey C(n)=C(⌊n/2⌋)+C(⌈n/2⌉)+n−1, with C(1)=0. At powers of two, C(n)=n log₂n−n+1. Random arrays can require fewer; do not overlay this as an exact expected curve.

Sorted input reduces insertion work, but this implementation still merges at each retained level; it has no already-sorted-merge shortcut. Extra space is one n-element buffer. The benchmark also keeps source, reference, and work arrays, totaling approximately 160 MB of integer storage at n=10m; this is benchmark memory, not the sort's auxiliary-space bound.

## Appendix C — Full results and refinement

Place `04_threshold_comparisons.png` and `05_refinement.png` here. Use `results/full/summary.csv` for the detailed table, and `selection.json` to show the search interval and locked choice. Explain which candidates are within 1% of the best measured CPU median; this descriptive band is not a statistical test.

Run `.venv/bin/python scripts/leaf_partitions.py` to inspect leaf sizes without sorting. At n=10m, S=48 and S=64 both stop at leaves of size 38 or 39. All thresholds from 39 through 75 create that same partition. This gives a structural explanation for identical comparison counts and cautions against overinterpreting the fine-search winner.

## Appendix D — Correctness evidence and limitations

- Optimized and sanitizer suites: empty, singleton, sorted, reversed, all-equal, duplicates, signed extrema, odd sizes, all sizes 0–260, multiple random trials and thresholds.
- Exact reference output comparison on every benchmark pass.
- Identical S=1/original comparison counts.
- Warm-ups, random order, excluded setup, separate counting.
- Limits: five seeds, timer resolution at small n, background load, cache effects, drift between coarse/refined phases, one machine and uniform distribution.
- Optional alternative-distribution studies were not run; propose them as future work, not completed evidence.

## Q&A — everyone should be able to answer

| Question | Answer |
|---|---|
| Why can insertion sort help despite O(n²)? | Its quadratic work is confined to small leaves; avoiding recursive calls and copying can outweigh extra comparisons. |
| Is the hybrid always faster? | No; threshold, implementation, distribution, hardware, and noise matter. Refer to held-out measurements. |
| Why is S=1 a useful check? | It produces the same recursion and merge work as ordinary merge sort. |
| What does S≥n do? | A single insertion sort; quadratic worst case. |
| Why does the count curve have plateaus? | Several thresholds can stop at exactly the same recursive subarray sizes. |
| Does the graph prove the complexity? | No. The derivation establishes the bound; observations check consistency. |
| Why not choose S by minimum comparisons? | CPU time also includes data movement and control overhead; runtime is our optimization objective. |
| Why separate counting and timing? | Counter increments change the work being timed. Compile-time specialization removes them. |
| Are IQRs confidence intervals? | No, they describe the middle half of the seed summaries. |
| Is the chosen S globally optimal? | No, it is the best measured candidate in the specified search. |
| Why fresh validation seeds? | They reduce the chance of reporting a tuning-data-specific advantage. |
| How is stability achieved? | Shift only strictly larger values; take the left key first on merge ties. |
| Why not benchmark std::sort instead? | The assignment asks for original merge sort; std::sort is only our correctness reference. |
| Why not skip an already ordered merge? | It would introduce another optimization and change the comparison being studied. |

## Rehearsal and ownership

For four members: assign slides 1–2, 3–4, 5–6, and 7–8. For three members: assign 1–3, 4–6, and 7–8. Adjust speaking load during rehearsal, but keep the timing budget unchanged. Each member should independently explain the comparison counter, the two complexity terms, the threshold selection, and the validation graph. Rehearse with a timer and leave the full two minutes for questions. Add team names before presenting.
