#!/usr/bin/env python3
"""Inspect recursion partitions without allocating or sorting any array."""
import argparse
from collections import Counter
from functools import lru_cache

@lru_cache(None)
def leaves(n, threshold):
    if n<=threshold or n<=1: return Counter({n:1})
    return leaves(n//2,threshold)+leaves(n-n//2,threshold)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--n',type=int,default=10000000)
    parser.add_argument('--thresholds',type=int,nargs='+',default=[32,48,64,96])
    args=parser.parse_args()
    if args.n<1 or any(s<1 for s in args.thresholds): parser.error('n and S must be positive')
    for s in args.thresholds:
        counts=leaves(args.n,s)
        assert sum(size*count for size,count in counts.items())==args.n
        print(f'n={args.n:,}, S={s}: '+', '.join(f'{count:,} leaves of size {size}' for size,count in sorted(counts.items())))
