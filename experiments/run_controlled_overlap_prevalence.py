#!/usr/bin/env python3
"""Controlled prevalence-by-overlap mechanism experiment.

This simulation varies class prevalence and Bayes-like overlap independently.
It is not counted as an additional health dataset.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from imblearn.over_sampling import RandomOverSampler, SMOTE
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "JMIR_SepAware" / "experiments" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def normalize(values):
    values = np.asarray(values, float)
    low, high = values.min(), values.max()
    return np.full(len(values), 0.5) if high == low else (values - low) / (high - low)


def sepaware_smote(x, y, seed):
    majority = int((y == 0).sum())
    minority = int((y == 1).sum())
    needed = majority - minority
    if needed <= 0:
        return x, y
    target_positive = minority + needed * 5
    strategy = {1: target_positive}
    pool_x, pool_y = SMOTE(random_state=seed, sampling_strategy=strategy).fit_resample(x, y)
    candidates = pool_x[len(x):]
    scaler = StandardScaler().fit(x)
    real = scaler.transform(x)
    candidate = scaler.transform(candidates)
    same = NearestNeighbors(n_neighbors=1).fit(real[y == 1]).kneighbors(candidate, return_distance=True)[0].ravel()
    opposite = NearestNeighbors(n_neighbors=1).fit(real[y == 0]).kneighbors(candidate, return_distance=True)[0].ravel()
    realism = NearestNeighbors(n_neighbors=1).fit(real).kneighbors(candidate, return_distance=True)[0].ravel()
    boundary = RandomForestClassifier(
        n_estimators=75, min_samples_leaf=3, class_weight="balanced", random_state=seed, n_jobs=1
    ).fit(x, y)
    confidence = boundary.predict_proba(candidates)[:, 1]
    score = (1 - normalize(realism)) + 0.5 * normalize(opposite - same) + 0.5 * normalize(confidence)
    selected = candidates[np.argsort(score)[-needed:]]
    return np.vstack([x, selected]), np.r_[y, np.ones(needed, dtype=int)]


def models(seed):
    return {
        "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed)),
        "RandomForest": RandomForestClassifier(n_estimators=100, min_samples_leaf=3, random_state=seed, n_jobs=1),
    }


rows = []
for prevalence in (0.05, 0.15, 0.30):
    for class_sep in (0.4, 1.0, 2.0):
        overlap = {0.4: "high", 1.0: "moderate", 2.0: "low"}[class_sep]
        for seed in range(10):
            x, y = make_classification(
                n_samples=2000, n_features=15, n_informative=8, n_redundant=3,
                n_clusters_per_class=2, weights=[1 - prevalence, prevalence],
                class_sep=class_sep, flip_y=0.02, random_state=1000 + seed,
            )
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.30, stratify=y, random_state=seed
            )
            variants = {"Real only": (x_train, y_train)}
            variants["Random oversampling"] = RandomOverSampler(random_state=seed).fit_resample(x_train, y_train)
            variants["SMOTE"] = SMOTE(random_state=seed).fit_resample(x_train, y_train)
            variants["SepAware-SMOTE"] = sepaware_smote(x_train, y_train, seed)
            for method, (train_x, train_y) in variants.items():
                for classifier, model in models(seed).items():
                    model.fit(train_x, train_y)
                    probability = model.predict_proba(x_test)[:, 1]
                    prediction = (probability >= 0.5).astype(int)
                    rows.append({
                        "prevalence": prevalence, "class_sep": class_sep, "overlap": overlap,
                        "seed": seed, "method": method, "classifier": classifier,
                        "auprc": average_precision_score(y_test, probability),
                        "macro_f1": f1_score(y_test, prediction, average="macro"),
                        "minority_f1": f1_score(y_test, prediction, pos_label=1),
                    })

results = pd.DataFrame(rows)
results.to_csv(OUT / "controlled_overlap_prevalence_long.csv", index=False)
summary = results.groupby(["prevalence", "class_sep", "overlap", "method", "classifier"], as_index=False).agg(
    auprc_mean=("auprc", "mean"), auprc_sd=("auprc", "std"),
    macro_f1_mean=("macro_f1", "mean"), minority_f1_mean=("minority_f1", "mean")
)
summary.to_csv(OUT / "controlled_overlap_prevalence_summary.csv", index=False)
model = smf.ols("auprc ~ C(method) * C(overlap) + C(method) * prevalence + C(classifier)", data=results).fit(cov_type="HC3")
(OUT / "controlled_overlap_prevalence_model.txt").write_text(model.summary().as_text())
pd.DataFrame({"term": model.params.index, "estimate": model.params.values, "p_value": model.pvalues.values}).to_csv(
    OUT / "controlled_overlap_prevalence_coefficients.csv", index=False
)
print(summary.to_string(index=False))
