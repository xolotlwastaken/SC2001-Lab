# Measured findings (SMOKE TEST ONLY)

- Machine: Apple M5; macOS-26.6.2-arm64-arm-64bit-Mach-O.
- Selected threshold: **S=50**, using tuning seeds only.
- Coarse winners by n: {'1000': 24, '10000': 48}.
- Refinement interval: [32, 64].
- Thresholds within 1% of the best measured tuning median: [50, 52]. This is a descriptive band, not a significance test.
- Held-out original merge CPU: **0.000254 s** (IQR 0.000252–0.000255).
- Held-out hybrid CPU: **0.000193 s** (IQR 0.000192–0.000194).
- Paired speedup, original/hybrid: **1.313×** (IQR 1.311–1.316); values above 1 favor hybrid.
- Median comparisons: original **120,420**; hybrid **183,609** (+52.47%).
- Fixed-S normalized comparison ratio ranges from 1.079 to 1.340 across sampled sizes.
- Every recorded sort passed an exact comparison with std::sort output.

## Interpretation safeguards

The selected threshold is the best observed candidate, not a universal optimum. Adjacent thresholds can yield identical recursion leaves and therefore identical comparison counts; timing differences within such groups are noise or execution variation. Five seeds and IQRs describe variation, not confidence intervals. Fine-search configurations were measured after the coarse sweep, so machine drift can affect selection. Held-out paired validation is the main evidence for the final performance claim. Small-n CPU measurements are sensitive to timer resolution.
