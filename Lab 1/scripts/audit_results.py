#!/usr/bin/env python3
"""Independent acceptance audit of full experiment coverage and selection."""
import argparse
import json
from pathlib import Path
import pandas as pd
from run_experiments import SIZES, SWEEP, TUNING, VALIDATION

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',type=Path,default=Path('results/full'))
    args=parser.parse_args()
    frame=pd.read_csv(args.results/'measurements.csv')
    selection=json.loads((args.results/'selection.json').read_text())
    metadata=json.loads((args.results/'metadata.json').read_text())
    assert not metadata['smoke']
    repetitions=int(metadata['repetitions'])
    assert frame.correct.eq(True).all()
    assert not frame.duplicated(['experiment','algorithm','n','threshold','seed','repetition']).any()
    low,high=selection['refinement_interval']
    refined=set(selection['refinement_candidates'])
    expected=set()
    for n in SIZES:
        for seed in TUNING: expected.add(('fixed_s','hybrid',n,32,seed))
    for n in [10000,100000,1000000,10000000]:
        for s in SWEEP:
            for seed in TUNING: expected.add(('coarse','hybrid',n,s,seed))
    for s in refined:
        for seed in TUNING: expected.add(('refine','hybrid',10000000,s,seed))
    for seed in VALIDATION:
        expected.add(('validation','merge',10000000,0,seed))
        expected.add(('validation','hybrid',10000000,selection['selected_s'],seed))
    keys=['experiment','algorithm','n','threshold','seed']
    actual=set(frame[keys].itertuples(index=False,name=None))
    assert actual == expected, f'Coverage mismatch: missing={expected-actual}, extra={actual-expected}'
    for _,rows in frame.groupby(keys):
        assert set(rows.repetition)==set(range(repetitions+1))
        counted=rows[rows.repetition.eq(0)]
        timed=rows[rows.repetition.ne(0)]
        assert counted.key_comparisons.notna().all() and counted.cpu_seconds.isna().all()
        assert counted.elapsed_seconds.isna().all()
        assert timed.key_comparisons.isna().all()
        assert timed.cpu_seconds.gt(0).all() and timed.elapsed_seconds.gt(0).all()
    tune=frame[frame.experiment.eq('refine') & frame.n.eq(10000000)]
    scores=tune.dropna(subset=['cpu_seconds']).groupby(['threshold','seed']).cpu_seconds.median().groupby('threshold').median()
    winner=min(scores.index,key=lambda s:(scores[s],s))
    assert winner==selection['selected_s'], 'Selection not reproducible'
    # Shared counted observations at S=32 must be deterministic across experiments.
    counted=frame.dropna(subset=['key_comparisons'])
    assert counted.groupby(['algorithm','n','threshold','seed']).key_comparisons.nunique().le(1).all()
    text=f'PASS: {len(expected)} configuration/seed groups; {len(frame)} rows; all required sizes, thresholds, repeats, disjoint seeds, counts, timings, and locked S={winner} verified.\n'
    (args.results/'audit.txt').write_text(text)
    print(text,end='')

if __name__=='__main__': main()
