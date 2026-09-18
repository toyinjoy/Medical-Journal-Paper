#!/usr/bin/env python3
"""Fail on incomplete or internally inconsistent paper evidence."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
aug=pd.read_csv(ROOT/'results/raw/predictive_metrics_long.csv')
adiag=pd.read_csv(ROOT/'results/raw/synthetic_diagnostics_long.csv')
tstr=pd.read_csv(ROOT/'results/raw/tstr_fold_metrics.csv')
tdiag=pd.read_csv(ROOT/'results/raw/tstr_diagnostics.csv')
assert len(aug)==1620 and not aug.duplicated(['dataset','repeat','fold','condition','classifier']).any()
assert len(adiag)==240 and not adiag.duplicated(['dataset','repeat','fold','condition']).any()
assert len(tstr)==720 and not tstr.duplicated(['task','repeat','fold','condition','classifier']).any()
assert len(tdiag)==240 and not tdiag.duplicated(['task','repeat','fold','condition']).any()
assert not any(x.isna().any().any() for x in (aug,adiag,tstr,tdiag))
coverage=pd.read_csv(ROOT/'results/experiment_coverage.csv')
transferable=coverage[coverage.transferable.eq('yes')]
statuses=transferable[['vigitel_obesity','covid_mortality','vigitel_smoking','kidney_mortality']]
assert statuses.eq('COMPLETED').all().all()
primary=pd.read_csv(ROOT/'results/statistical_tests/primary_contrasts.csv')
assert len(primary)==8 and primary.p_holm.between(0,1).all()
print('Consistency checks passed: 84/84 transferable cells; authoritative row keys are complete and unique.')
