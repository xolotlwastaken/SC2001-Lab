# Measured findings 

- Machine: Apple M5; macOS-26.6.2-arm64-arm-64bit-Mach-O.
- Selected threshold: **S=64**, using tuning seeds only.
- Coarse winners by n: {'10000': 48, '100000': 96, '1000000': 32, '10000000': 64}.
- Refinement interval: [48, 96].
- Thresholds within 1% of the best measured tuning median: [32, 48, 64]. This is a descriptive band, not a significance test.
- Minimum median comparison count among tested candidates at n=10,000,000: **S=1** (smallest threshold breaks ties).
- Candidates matching the selected threshold's comparison counts on every tuning seed: [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]. Matching counts alone do not prove structural equivalence; inspect the recursive leaf sizes.
- Held-out original merge CPU: **0.443770 s** (IQR 0.443461–0.443864).
- Held-out hybrid CPU: **0.386277 s** (IQR 0.385783–0.389874).
- Paired speedup, original/hybrid: **1.147×** (IQR 1.138–1.152); values above 1 favor hybrid.
- Median comparisons: original **220,101,526**; hybrid **281,233,315** (+27.77%).
- Fixed-S normalized comparison ratio ranges from 1.042 to 1.343 across sampled sizes.
- Every recorded sort passed an exact comparison with std::sort output.

## Interpretation safeguards

The selected threshold is the best observed candidate, not a universal optimum. Adjacent thresholds can yield identical recursion leaves and therefore identical comparison counts; timing differences within such groups are noise or execution variation. Five seeds and IQRs describe variation, not confidence intervals. Fine-search configurations were measured after the coarse sweep, so machine drift can affect selection. The refinement plot separates the two phases: systematic differences within an equivalent-work plateau must not be attributed to S alone. Held-out paired validation is the main evidence for the final performance claim. Small-n CPU measurements are sensitive to timer resolution.
