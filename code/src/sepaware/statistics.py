from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import t
from statsmodels.stats.multitest import multipletests


def nadeau_bengio(differences, *, train_fraction: float = 0.8, test_fraction: float = 0.2):
    """Nadeau-Bengio corrected interval/test for repeated-CV fold summaries."""
    d=np.asarray(differences, float); n=len(d); mean=float(d.mean()); variance=float(d.var(ddof=1))
    correction=(1/n)+(test_fraction/train_fraction)
    se=float(np.sqrt(correction*variance)); df=n-1
    statistic=mean/se if se else np.inf*np.sign(mean)
    p=float(2*t.sf(abs(statistic), df)) if se else 0.0
    half=float(t.ppf(.975,df)*se) if se else 0.0
    effect=mean/np.sqrt(variance) if variance else np.inf*np.sign(mean)
    return mean, mean-half, mean+half, p, effect


def primary_contrasts(frame: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for dataset in frame.dataset.unique():
        for generator in ("CTGAN","TVAE"):
            keys=["dataset","repeat","fold","classifier"]
            a=frame[(frame.dataset==dataset)&(frame.condition==f"SepAware {generator}")][keys+["auprc"]]
            b=frame[(frame.dataset==dataset)&(frame.condition==f"Standard {generator}")][keys+["auprc"]]
            joined=a.merge(b,on=keys,suffixes=("_sep","_std")); joined["difference"]=joined.auprc_sep-joined.auprc_std
            # Classifiers share the same fold and candidate pool, so average them
            # before inference; the 15 repeated-CV fold summaries remain dependent.
            fold=joined.groupby(["repeat","fold"]).difference.mean()
            mean,low,high,p,effect=nadeau_bengio(fold)
            rows.append({"dataset":dataset,"contrast":f"SepAware {generator} - Standard {generator}","mean_difference":mean,"ci_lower":low,"ci_upper":high,"p_unadjusted":p,"effect_size_d":effect,"n_paired_fold_classifier":len(joined),"n_fold_summaries":len(fold),"n_repetitions":joined.repeat.nunique(),"direction":"improvement" if mean>0 else "decrease"})
    out=pd.DataFrame(rows); out["p_holm"]=multipletests(out.p_unadjusted,method="holm")[1]; return out


def contrast_sensitivity(frame: pd.DataFrame) -> pd.DataFrame:
    """Descriptive SepAware-minus-standard AUPRC effects by classifier/repetition."""
    rows=[]
    keys=["dataset","repeat","fold","classifier"]
    for dataset in frame.dataset.unique():
        for generator in ("CTGAN","TVAE"):
            a=frame[(frame.dataset==dataset)&(frame.condition==f"SepAware {generator}")][keys+["auprc"]]
            b=frame[(frame.dataset==dataset)&(frame.condition==f"Standard {generator}")][keys+["auprc"]]
            paired=a.merge(b,on=keys,suffixes=("_sep","_std"))
            paired["difference"]=paired.auprc_sep-paired.auprc_std
            for (classifier,repeat), group in paired.groupby(["classifier","repeat"]):
                rows.append({"dataset":dataset,"generator":generator,"classifier":classifier,
                             "repeat":repeat,"n_folds":len(group),
                             "mean_difference":group.difference.mean(),
                             "sd_difference":group.difference.std(ddof=1)})
    return pd.DataFrame(rows)


def factorial_effects(by_fold: pd.DataFrame) -> pd.DataFrame:
    """Fold-paired factorial effects with t intervals; inference is exploratory."""
    mapping={"separability_main_effect":"separability",
             "anchor_main_effect":"anchor",
             "interaction_difference_in_differences":"interaction"}
    rows=[]
    macro=by_fold[by_fold.metric.eq("Macro_F1")]
    for dataset, group in macro.groupby("dataset_group"):
        for column,effect in mapping.items():
            values=group[column].dropna().to_numpy(float); n=len(values)
            mean=float(values.mean()); sd=float(values.std(ddof=1)); se=sd/np.sqrt(n)
            half=float(t.ppf(.975,n-1)*se); stat=mean/se if se else np.inf*np.sign(mean)
            p=float(2*t.sf(abs(stat),n-1)) if se else 0.0
            rows.append({"dataset":dataset,"effect":effect,"estimate":mean,
                         "ci_lower":mean-half,"ci_upper":mean+half,
                         "p_unadjusted":p,"n_fold_blocks":n,
                         "scale":"Macro-F1 difference","inference":"exploratory"})
    return pd.DataFrame(rows)
