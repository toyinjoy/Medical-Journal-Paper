#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'code'/'src'))
from sepaware.statistics import primary_contrasts, contrast_sensitivity, factorial_effects

source=ROOT/'results'/'raw'/'augmentation_fold_metrics.csv'
if not source.exists(): source=ROOT/'results'/'raw'/'predictive_metrics_long.csv'
frame=pd.read_csv(source).rename(columns={"minority_f1":"positive_f1","minority_precision":"positive_precision","minority_recall":"positive_recall"})
out=ROOT/'results'/'statistical_tests'; out.mkdir(parents=True,exist_ok=True)
result=primary_contrasts(frame)
result.to_csv(out/'primary_contrasts.csv',index=False)
result[["dataset","contrast","p_unadjusted","p_holm"]].to_csv(out/'multiplicity_adjusted_results.csv',index=False)
contrast_sensitivity(frame).to_csv(out/'primary_contrast_sensitivity.csv',index=False)
factorial_source=ROOT/'results'/'factorial'/'factorial_effects_by_fold.csv'
if factorial_source.exists():
    factorial_effects(pd.read_csv(factorial_source)).to_csv(out/'factorial_effects.csv',index=False)
print(result.to_string(index=False))
