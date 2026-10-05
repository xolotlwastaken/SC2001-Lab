# Measured findings 

- Machine: Apple M5; macOS-26.6.2-arm64-arm-64bit-Mach-O.
- Selected threshold: **S=192**, using tuning seeds only.
- Coarse winners by n: {'10000': 192, '100000': 192, '1000000': 96, '10000000': 256}.
- Refinement interval: [192, 384], testing distinct-partition representatives [192, 305, 306].
- Thresholds within 1% of the best measured tuning median: [192]. This is a descriptive band, not a significance test.
- Minimum median comparison count among tested candidates at n=10,000,000: **S=1** (smallest threshold breaks ties).
- Candidates matching the selected threshold's comparison counts on every tuning seed: [192, 256]. Matching counts alone do not prove structural equivalence; inspect the recursive leaf sizes.
- Held-out original merge CPU: **0.841846 s** (IQR 0.841275–0.850693).
- Held-out hybrid CPU: **0.655154 s** (IQR 0.651119–0.746257).
- Paired speedup, original/hybrid: **1.293×** (IQR 1.126–1.294); values above 1 favor hybrid.
- Median comparisons: original **220,101,526**; hybrid **548,538,181** (+149.22%).
- Fixed-S normalized comparison ratio ranges from 1.042 to 1.343 across sampled sizes.
- Every recorded sort passed an exact comparison with Arrays.sort output.

## Interpretation safeguards

The selected threshold is the best observed distinct recursion partition, not a universal optimum. Adjacent thresholds can yield identical recursion leaves and therefore identical work; the refinement tests one representative per distinct partition. Five seeds and IQRs describe variation, not confidence intervals. Held-out paired validation is the main evidence for the final performance claim. Small-n CPU measurements are sensitive to timer resolution.
