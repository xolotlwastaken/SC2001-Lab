#!/usr/bin/env python3
"""Sequential, checkpointed benchmark orchestration. No concurrent timing jobs."""
import argparse
import csv
import hashlib
import io
import json
import platform
import random
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA_SOURCES = [
    ROOT / 'src' / 'Sorting.java',
    ROOT / 'src' / 'MersenneTwister.java',
    ROOT / 'src' / 'Benchmark.java',
]
SIZES = [1000, 3000, 10000, 30000, 100000, 300000, 1000000, 3000000, 10000000]
SWEEP = [1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128, 192, 256,
         384, 512, 768, 1024, 1536, 2048]
TUNING = [101, 202, 303, 404, 505]
VALIDATION = [1101, 1202, 1303, 1404, 1505]
FIELDS = ['experiment', 'algorithm', 'n', 'threshold', 'seed', 'repetition',
          'key_comparisons', 'cpu_seconds', 'elapsed_seconds', 'correct']

def leaf_signature(n, threshold):
    """Return the recursive leaf-size multiset without allocating an input array."""
    pending = [n]
    counts = {}
    while pending:
        size = pending.pop()
        if size <= threshold or size <= 1:
            counts[size] = counts.get(size, 0) + 1
        else:
            left = size // 2
            pending.extend((left, size - left))
    return tuple(sorted(counts.items()))

def structural_candidates(n, low, high):
    """Keep one threshold for each distinct recursion partition in the interval."""
    candidates = []
    previous = None
    for threshold in range(low, high + 1):
        signature = leaf_signature(n, threshold)
        if signature != previous:
            candidates.append(threshold)
            previous = signature
    return candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true', help='Small pipeline check; not lab evidence')
    parser.add_argument('--output', type=Path, default=ROOT / 'results' / 'full')
    parser.add_argument('--cpu-label', help='Verified CPU model when sandbox blocks sysctl')
    parser.add_argument('--repetitions', type=int, default=5,
                        help='Timed repetitions per seed and configuration (default: 5)')
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error('--repetitions must be positive')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    shards = out / 'shards'
    shards.mkdir(exist_ok=True)
    binary = ROOT / 'build' / 'Benchmark.class'
    benchmark_command = ['java', '-cp', str(ROOT / 'build'), 'Benchmark']
    fingerprint_paths = [binary, *JAVA_SOURCES,
                         ROOT/'scripts/run_experiments.py', ROOT/'Makefile']
    fingerprints = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in fingerprint_paths}
    java_version = subprocess.run(
        ['java', '-version'], text=True, capture_output=True, check=True)
    config = {'smoke': args.smoke, 'fingerprints': fingerprints, 'platform': platform.platform(),
              'machine': platform.machine(),
              'compiler': (java_version.stderr or java_version.stdout).strip(),
              'flags': 'javac --release 17',
              'rng': 'MT19937; rejection at floor(2^32/10000000)*10000000; 1+v%10000000',
              'timer': 'ThreadMXBean current-thread CPU time; System.nanoTime elapsed',
              'tuning_seeds': TUNING, 'validation_seeds': VALIDATION,
              'cpu': args.cpu_label or platform.processor() or 'unknown; supply --cpu-label',
              'repetitions': args.repetitions, 'x': 10000000,
              'coarse_thresholds': SWEEP}
    metadata = out/'metadata.json'
    if metadata.exists() and json.loads(metadata.read_text()) != config:
        raise SystemExit('Configuration/build changed: choose a new output directory.')
    metadata.write_text(json.dumps(config, indent=2)+'\n')
    tuning = TUNING[:2] if args.smoke else TUNING
    validation = VALIDATION[:2] if args.smoke else VALIDATION
    sizes = [1000,3000,10000] if args.smoke else SIZES
    tuning_sizes = [1000,10000] if args.smoke else [10000,100000,1000000,10000000]
    target = tuning_sizes[-1]
    all_rows = []

    def run_phase(name, jobs):
        random.Random(771).shuffle(jobs)
        for n, seed, thresholds in jobs:
            signature = hashlib.sha256(str(thresholds).encode()).hexdigest()[:10]
            path = shards/f'{name}-{n}-{seed}-{signature}.csv'
            if not path.exists():
                print(f'{name}: n={n:,}, seed={seed}, S={thresholds}', flush=True)
                order_seed = int(hashlib.sha256(f'{name}:{n}:{seed}'.encode()).hexdigest()[:8],16)
                result = subprocess.run(benchmark_command + [str(n), str(seed), str(args.repetitions),
                                         ','.join(map(str,thresholds)), str(order_seed)],
                                        text=True, capture_output=True, check=True)
                rows = list(csv.DictReader(io.StringIO(','.join(FIELDS[1:])+'\n'+result.stdout)))
                expected_rows = len(thresholds) * (args.repetitions + 1)
                if len(rows) != expected_rows or any(r['correct']!='true' for r in rows):
                    raise RuntimeError('Incomplete or incorrect benchmark output')
                temporary = path.with_suffix('.tmp')
                with temporary.open('w',newline='') as f:
                    writer=csv.DictWriter(f,fieldnames=FIELDS)
                    writer.writeheader()
                    writer.writerows(dict(experiment=name,**r) for r in rows)
                temporary.replace(path)
            with path.open() as f: all_rows.extend(csv.DictReader(f))

    def scores(experiments, n):
        grouped = {}
        for r in all_rows:
            if r['experiment'] in experiments and int(r['n']) == n and r['cpu_seconds']:
                grouped.setdefault((int(r['threshold']),int(r['seed'])),[]).append(float(r['cpu_seconds']))
        by_threshold = {}
        for (s,seed), values in grouped.items():
            by_threshold.setdefault(s,[]).append(statistics.median(values))
        return {s:statistics.median(values) for s,values in by_threshold.items()}

    run_phase('fixed_s',[(n,seed,[32]) for n in sizes for seed in tuning])
    run_phase('coarse',[(n,seed,SWEEP) for n in tuning_sizes for seed in tuning])
    coarse = scores({'coarse'},target)
    winner = min(coarse,key=lambda s:(coarse[s],s))
    i = SWEEP.index(winner)
    if i == 0 or i == len(SWEEP) - 1:
        raise RuntimeError(
            f'Coarse winner S={winner} is on the search boundary; extend SWEEP.')
    low, high = SWEEP[max(0,i-1)], SWEEP[min(len(SWEEP)-1,i+1)]
    # Retest one representative from every distinct recursion partition in a
    # single randomized phase. This avoids comparing identical-work thresholds
    # or mixing earlier coarse timing with later refinement timing.
    refined = structural_candidates(target, low, high)
    run_phase('refine',[(target,seed,refined) for seed in tuning])
    candidates = scores({'refine'},target)
    selected = min(candidates,key=lambda s:(candidates[s],s))
    selection = {'target_n':target, 'coarse_winner':winner, 'refinement_interval':[low,high],
                 'refinement_candidates': refined,
                 'selected_s':selected, 'objective':'median across seeds of median repeated CPU seconds',
                 'coarse_winners_by_n':{str(n):min(scores({'coarse'},n),key=lambda s:(scores({'coarse'},n)[s],s))
                                        for n in tuning_sizes},
                 'candidate_cpu_seconds':dict(sorted(candidates.items()))}
    # Persist the choice before any held-out validation is performed.
    (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    print(f'Locked S={selected}; starting held-out validation.',flush=True)
    run_phase('validation',[(target,seed,[0,selected]) for seed in validation])
    with (out/'measurements.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS); writer.writeheader(); writer.writerows(all_rows)
    print(f'Complete: {len(all_rows)} rows in {out}',flush=True)

if __name__ == '__main__': main()
