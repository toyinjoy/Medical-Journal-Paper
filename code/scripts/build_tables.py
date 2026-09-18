#!/usr/bin/env python3
"""Build manuscript tables exclusively from authoritative result CSV files."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
raw=ROOT/'results'/'raw'; out=ROOT/'results'/'tables'; tex=ROOT/'tables'
out.mkdir(parents=True,exist_ok=True); tex.mkdir(exist_ok=True)

aug=pd.read_csv(raw/'predictive_metrics_long.csv').rename(columns={
    'minority_f1':'positive_f1','minority_precision':'positive_precision',
    'minority_recall':'positive_recall'})
metrics=['auprc','auroc','macro_f1','positive_f1','positive_precision',
         'positive_recall','balanced_accuracy','brier','calibration_intercept',
         'calibration_slope']
summary=aug.groupby(['dataset','condition'])[metrics].agg(['mean','std']).reset_index()
summary.columns=['_'.join(c).rstrip('_') for c in summary.columns]
summary.to_csv(out/'augmentation_metric_summary.csv',index=False)

primary=summary[['dataset','condition','auprc_mean','auprc_std','macro_f1_mean',
                 'positive_recall_mean','brier_mean']].copy()
primary.to_csv(out/'common_benchmark_primary.csv',index=False)
lines=[r'\begin{longtable}{p{.17\textwidth}p{.24\textwidth}rrrrr}',
       r'\caption{Common augmentation benchmark. Values are means over 3 repeated 5-fold partitions and 3 classifiers (45 paired fold--classifier observations per method and task). Held-out real folds retain natural prevalence; uncertainty and paired inference are reported separately.}\label{tab:common-benchmark}\\',
       r'\toprule',r'Task & Method & AUPRC & Macro-F1 & Recall & Brier & $n$ \\',r'\midrule',r'\endfirsthead',
       r'\toprule',r'Task & Method & AUPRC & Macro-F1 & Recall & Brier & $n$ \\',r'\midrule',r'\endhead']
for _,r in primary.iterrows():
    lines.append(f"{r.dataset} & {r.condition} & {r.auprc_mean:.3f} & {r.macro_f1_mean:.3f} & {r.positive_recall_mean:.3f} & {r.brier_mean:.3f} & 45 \\\\")
lines += [r'\bottomrule',r'\end{longtable}']
(tex/'common_benchmark_primary.tex').write_text('\n'.join(lines)+'\n')

if (raw/'tstr_fold_metrics.csv').exists():
    t=pd.read_csv(raw/'tstr_fold_metrics.csv').rename(columns={'minority_f1':'positive_f1','minority_precision':'positive_precision','minority_recall':'positive_recall'})
    ts=t.groupby(['dataset','condition'])[metrics].agg(['mean','std']).reset_index()
    ts.columns=['_'.join(c).rstrip('_') for c in ts.columns]
    ts.to_csv(out/'tstr_metric_summary.csv',index=False)
    show=ts[['dataset','condition','auprc_mean','macro_f1_mean','positive_recall_mean','brier_mean']]
    lines=[r'\begin{longtable}{p{.20\textwidth}p{.24\textwidth}rrrr}',
           r'\caption{TSTR performance. Values are means over 3 repeated 5-fold partitions and 3 classifiers (45 paired observations per condition and task). Synthetic class counts match each real training fold; evaluation uses held-out real records.}\label{tab:tstr-summary}\\',
           r'\toprule',r'Task & Synthetic training data & AUPRC & Macro-F1 & Recall & Brier \\',r'\midrule',r'\endfirsthead',
           r'\toprule',r'Task & Synthetic training data & AUPRC & Macro-F1 & Recall & Brier \\',r'\midrule',r'\endhead']
    for _,r in show.iterrows():
        lines.append(f"{r.dataset} & {r.condition} & {r.auprc_mean:.3f} & {r.macro_f1_mean:.3f} & {r.positive_recall_mean:.3f} & {r.brier_mean:.3f} \\\\")
    lines += [r'\bottomrule',r'\end{longtable}']
    (tex/'tstr_summary.tex').write_text('\n'.join(lines)+'\n')
if (raw/'tstr_diagnostics.csv').exists():
    d=pd.read_csv(raw/'tstr_diagnostics.csv')
    d.groupby(['dataset','condition']).agg({c:['mean','std'] for c in ['marginal_similarity','correlation_similarity','detection_auroc','coverage_distance','diversity','exact_match_rate','membership_proxy_auroc']}).to_csv(out/'tstr_diagnostic_summary.csv')
