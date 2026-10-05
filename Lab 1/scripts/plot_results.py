#!/usr/bin/env python3
"""Regenerate figures and numeric slide evidence from recorded CSV only."""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1]/'build'/'mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':12, 'axes.spines.top':False, 'axes.spines.right':False,
                     'figure.dpi':120, 'savefig.dpi':240, 'axes.titleweight':'bold'})
BLUE, ORANGE = '#176B9B', '#D96B27'

def summary(frame, keys, metric):
    # First reduce repetitions within seeds. Each seed then has equal weight.
    per_seed=frame.dropna(subset=[metric]).groupby(keys+['seed'])[metric].median()
    return per_seed.groupby(level=list(range(len(keys)))).agg(
        median='median', q1=lambda x:x.quantile(.25), q3=lambda x:x.quantile(.75)).reset_index()

def curve(ax, data, x, label=None, color=BLUE):
    data=data.sort_values(x)
    ax.plot(data[x],data['median'],marker='o',ms=4,label=label,color=color)
    ax.fill_between(data[x],data.q1,data.q3,color=color,alpha=.16)
    ax.grid(alpha=.18)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',type=Path,default=ROOT/'results/full')
    parser.add_argument('--output',type=Path,default=ROOT/'figures')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(args.results/'measurements.csv')
    metadata=json.loads((args.results/'metadata.json').read_text())
    selection=json.loads((args.results/'selection.json').read_text())
    if not df.correct.eq(True).all(): raise ValueError('Unvalidated measurements')
    runtime = metadata.get('compiler', 'unknown').splitlines()[0]
    toolchain = f'{runtime} · {metadata.get("flags", "")}'
    reference_sort = 'Arrays.sort' if metadata.get('flags', '').startswith('javac') else 'std::sort'
    def save(fig,name):
        footer='SMOKE TEST — NOT LAB RESULTS' if metadata['smoke'] else 'Median across 5 seeds; shading/error bars = interquartile range'
        fig.text(.5,.012,footer,ha='center',fontsize=9,color='#555555')
        fig.tight_layout(rect=(0,.04,1,1))
        for extension in ['png','pdf']: fig.savefig(args.output/f'{name}.{extension}')
        plt.close(fig)

    fixed=summary(df[df.experiment.eq('fixed_s')],['n'],'key_comparisons')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    curve(axes[0],fixed,'n',label='Measured, S=32')
    scale=fixed.iloc[-1]['median']/(fixed.iloc[-1]['n']*np.log2(fixed.iloc[-1]['n']))
    axes[0].plot(fixed.n,scale*fixed.n*np.log2(fixed.n),'--',color=ORANGE,label='Scaled n log₂ n reference')
    axes[0].set(xscale='log',yscale='log',xlabel='Input size n',ylabel='Key comparisons',title='Fixed threshold: growth with n')
    axes[0].legend(fontsize=9)
    normalized=fixed.copy()
    for column in ['median','q1','q3']: normalized[column]/=fixed.n*np.log2(fixed.n)
    curve(axes[1],normalized,'n')
    axes[1].set(xscale='log',xlabel='Input size n',ylabel='C / (n log₂ n)',title='Normalized comparison count')
    save(fig,'01_fixed_s')

    coarse=df[df.experiment.eq('coarse')]
    fixed_n=100000 if not metadata['smoke'] else 10000
    counts=summary(coarse[coarse.n.eq(fixed_n)],['threshold'],'key_comparisons')
    fig,ax=plt.subplots(figsize=(9,4.8)); curve(ax,counts,'threshold')
    ax.set(xlabel='Insertion-sort threshold S',ylabel='Key comparisons',title=f'Fixed n = {fixed_n:,}: comparisons versus S')
    save(fig,'02_fixed_n')

    ns=sorted(coarse.n.unique())
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for ax,n in zip(axes.flat,ns):
        data=summary(coarse[coarse.n.eq(n)],['threshold'],'cpu_seconds')
        curve(ax,data,'threshold')
        best=data.sort_values(['median','threshold']).iloc[0]
        ax.scatter([best.threshold],[best['median']],color=ORANGE,zorder=5,s=55)
        ax.set(title=f'n = {n:,}; coarse winner S={int(best.threshold)}',xlabel='Threshold S',ylabel='CPU time (seconds)')
    for ax in list(axes.flat)[len(ns):]: ax.set_visible(False)
    save(fig,'03_threshold_cpu')

    fig,ax=plt.subplots(figsize=(9,5))
    for n,color in zip(ns,['#176B9B','#D96B27','#23826B','#855CA6']):
        data=summary(coarse[coarse.n.eq(n)],['threshold'],'key_comparisons')
        for column in ['median','q1','q3']: data[column]/=n
        curve(ax,data,'threshold',label=f'n={n:,}',color=color)
    ax.set(xlabel='Threshold S',ylabel='Key comparisons per element',title='Comparison cost across input sizes'); ax.legend()
    save(fig,'04_threshold_comparisons')

    target=selection['target_n']; selected=selection['selected_s']
    tuned=df[df.experiment.eq('refine') & df.n.eq(target)]
    refined=summary(tuned,['threshold'],'cpu_seconds')
    low,high=selection['refinement_interval']
    fig,ax=plt.subplots(figsize=(10,5))
    curve(ax,refined,'threshold',label='Distinct recursion partitions')
    ax.axvline(selected,color='#555555',ls='--',label=f'Selected S={selected}')
    ax.set(xlabel='Threshold S',ylabel='CPU time (seconds)',title=f'Refined tuning at n={target:,}'); ax.legend()
    save(fig,'05_refinement')

    validation=df[df.experiment.eq('validation')]
    table=summary(validation,['algorithm'],'cpu_seconds').rename(columns={'median':'cpu_median','q1':'cpu_q1','q3':'cpu_q3'})
    table=table.merge(summary(validation,['algorithm'],'key_comparisons').rename(columns={
        'median':'comparisons_median','q1':'comparisons_q1','q3':'comparisons_q3'}),on='algorithm').set_index('algorithm').loc[['merge','hybrid']]
    table.to_csv(args.results/'validation_summary.csv')
    paired=validation.dropna(subset=['cpu_seconds']).groupby(['seed','algorithm']).cpu_seconds.median().unstack()
    ratios=paired['merge']/paired['hybrid']
    speedup=float(ratios.median())
    change=float(100*(table.loc['hybrid','comparisons_median']/table.loc['merge','comparisons_median']-1))
    fig,axes=plt.subplots(1,2,figsize=(11,5))
    for ax,metric,title,ylabel in [(axes[0],'cpu','CPU time','Seconds'),(axes[1],'comparisons','Key comparisons','Comparisons')]:
        values=table[metric+'_median'].to_numpy()
        errors=np.stack([values-table[metric+'_q1'].to_numpy(),table[metric+'_q3'].to_numpy()-values])
        ax.bar(['Original merge',f'Hybrid S={selected}'],values,color=[BLUE,ORANGE],yerr=errors,capsize=5)
        ax.set(title=title,ylabel=ylabel,ylim=(0,float(max(values+errors[1])*1.2)))
        for i,v in enumerate(values): ax.text(i,v*1.03,f'{v:,.4f}' if metric=='cpu' else f'{v:,.0f}',ha='center',fontsize=10)
    fig.suptitle(f'Held-out n={target:,}: paired median speedup {speedup:.3f}×; comparisons {change:+.1f}%')
    save(fig,'06_validation')

    full_summary=[]
    for metric in ['cpu_seconds','key_comparisons','elapsed_seconds']:
        part=summary(df,['experiment','algorithm','n','threshold'],metric); part['metric']=metric; full_summary.append(part)
    pd.concat(full_summary).to_csv(args.results/'summary.csv',index=False)
    near=refined[refined['median']<=refined['median'].min()*1.01].threshold.astype(int).tolist()
    count_candidates=coarse[coarse.n.eq(target)].dropna(subset=['key_comparisons']).pivot(
        index='seed',columns='threshold',values='key_comparisons')
    equal_counts=[int(s) for s in count_candidates if count_candidates[s].equals(count_candidates[selected])]
    count_medians=count_candidates.median()
    comparison_winner=int(min(count_medians.index,key=lambda s:(count_medians[s],s)))
    report=f'''# Measured findings {'(SMOKE TEST ONLY)' if metadata['smoke'] else ''}

- Machine: {metadata['cpu']}; {metadata['platform']}.
- Selected threshold: **S={selected}**, using tuning seeds only.
- Coarse winners by n: {selection['coarse_winners_by_n']}.
- Refinement interval: [{low}, {high}], testing distinct-partition representatives {selection['refinement_candidates']}.
- Thresholds within 1% of the best measured tuning median: {near}. This is a descriptive band, not a significance test.
- Minimum median comparison count among tested candidates at n={target:,}: **S={comparison_winner}** (smallest threshold breaks ties).
- Candidates matching the selected threshold's comparison counts on every tuning seed: {equal_counts}. Matching counts alone do not prove structural equivalence; inspect the recursive leaf sizes.
- Held-out original merge CPU: **{table.loc['merge','cpu_median']:.6f} s** (IQR {table.loc['merge','cpu_q1']:.6f}–{table.loc['merge','cpu_q3']:.6f}).
- Held-out hybrid CPU: **{table.loc['hybrid','cpu_median']:.6f} s** (IQR {table.loc['hybrid','cpu_q1']:.6f}–{table.loc['hybrid','cpu_q3']:.6f}).
- Paired speedup, original/hybrid: **{speedup:.3f}×** (IQR {ratios.quantile(.25):.3f}–{ratios.quantile(.75):.3f}); values above 1 favor hybrid.
- Median comparisons: original **{table.loc['merge','comparisons_median']:,.0f}**; hybrid **{table.loc['hybrid','comparisons_median']:,.0f}** ({change:+.2f}%).
- Fixed-S normalized comparison ratio ranges from {normalized['median'].min():.3f} to {normalized['median'].max():.3f} across sampled sizes.
- Every recorded sort passed an exact comparison with {reference_sort} output.

## Interpretation safeguards

The selected threshold is the best observed distinct recursion partition, not a universal optimum. Adjacent thresholds can yield identical recursion leaves and therefore identical work; the refinement tests one representative per distinct partition. Five seeds and IQRs describe variation, not confidence intervals. Held-out paired validation is the main evidence for the final performance claim. Small-n CPU measurements are sensitive to timer resolution.
'''
    (args.results/'findings.md').write_text(report)
    if not metadata['smoke']:
        content=f'''# Measured slide content — full assignment run

These statements are generated from the selected full-run `measurements.csv`. Refer to the blueprint for speaker notes and timings.

## Slide 4: method footer

**{metadata['cpu']} · {toolchain} · uniform integers [1, 10⁷] · five seeds × {metadata['repetitions']} repetitions.**

## Slide 5: result headline

**At S=32, comparison growth is consistent with n log₂n scaling over the tested sizes.**

The normalized ratio C/(n log₂n) ranges from **{normalized['median'].min():.3f} to {normalized['median'].max():.3f}**. This is empirical consistency, not a proof of the bound.

## Slide 6: result callout

**Selected S={selected} after coarse search and partition-aware refinement at 10 million elements.**

Coarse winners: {selection['coarse_winners_by_n']}. Refined interval: [{low}, {high}], with distinct-partition representatives {selection['refinement_candidates']}. Candidates within 1% of the best median: {near}. Describe this as a measured fast region; do not claim each tiny timing difference is meaningful.

The comparison-count winner at 10 million is **S={comparison_winner}**, while the CPU-time winner is **S={selected}**. Candidates with identical observed comparison counts to the selected threshold: {equal_counts}.

The refinement phase retests comparable structural candidates together and avoids ranking thresholds that produce identical recursion leaves. The held-out hybrid-versus-original comparison supports the final speedup claim.

## Slide 7: result headline

**Hybrid S={selected}: {speedup:.3f}× paired median speedup; {change:+.1f}% key comparisons on fresh data.**

| Measurement | Original merge | Hybrid |
|---|---:|---:|
| Median CPU seconds | {table.loc['merge','cpu_median']:.6f} | {table.loc['hybrid','cpu_median']:.6f} |
| CPU IQR | {table.loc['merge','cpu_q1']:.6f}–{table.loc['merge','cpu_q3']:.6f} | {table.loc['hybrid','cpu_q1']:.6f}–{table.loc['hybrid','cpu_q3']:.6f} |
| Median key comparisons | {table.loc['merge','comparisons_median']:,.0f} | {table.loc['hybrid','comparisons_median']:,.0f} |

Paired speedup IQR: **{ratios.quantile(.25):.3f}–{ratios.quantile(.75):.3f}×**. Speedup above 1 favors hybrid; below 1 favors original merge.

## Slide 8: three conclusions

1. Correctness: the Java correctness suite passed; every recorded sort matched its reference.
2. Complexity: fixed-S measurements are consistent with the derived n log n growth; threshold changes affect both leaf work and merge levels.
3. Performance: on this machine and distribution, the selected hybrid achieved **{speedup:.3f}×** paired median speedup with **{change:+.1f}%** comparisons.

**Limitation:** this is a measured threshold for one implementation and environment, with five held-out datasets; it is not a universal optimum.
'''
        (ROOT/'slides'/'measured_content.md').write_text(content)
    print(report)

if __name__=='__main__': main()
