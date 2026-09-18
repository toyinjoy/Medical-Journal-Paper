#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]; raw=ROOT/'results'/'raw'; figures=ROOT/'figures'; figures.mkdir(exist_ok=True)
d=pd.read_csv(raw/'predictive_metrics_long.csv')
means=d.groupby(['dataset','condition']).auprc.mean().unstack()
order=['Real only','Random oversampling','Random undersampling','SMOTE','Class weighted','Standard CTGAN','SepAware CTGAN','Standard TVAE','SepAware TVAE']
means=means[[c for c in order if c in means]]
ax=means.plot.bar(figsize=(10,5),width=.86); ax.set_ylabel('Held-out-real AUPRC'); ax.set_xlabel('Outcome task'); ax.legend(fontsize=7,ncol=3); plt.xticks(rotation=15,ha='right'); plt.tight_layout()
plt.savefig(figures/'common_benchmark_auprc.pdf'); plt.savefig(figures/'common_benchmark_auprc.png',dpi=240); plt.close()

stats=pd.read_csv(ROOT/'results'/'statistical_tests'/'primary_contrasts.csv')
stats['label']=stats.dataset+' / '+stats.contrast.str.extract(r'SepAware (CTGAN|TVAE)')[0]
y=range(len(stats)); plt.figure(figsize=(7,4.5)); plt.errorbar(stats.mean_difference,y,xerr=[stats.mean_difference-stats.ci_lower,stats.ci_upper-stats.mean_difference],fmt='o',capsize=3); plt.axvline(0,color='black',lw=.8); plt.yticks(list(y),stats.label); plt.xlabel('Paired AUPRC difference (SepAware − standard)'); plt.tight_layout(); plt.savefig(figures/'primary_contrasts.pdf'); plt.savefig(figures/'primary_contrasts.png',dpi=240); plt.close()
