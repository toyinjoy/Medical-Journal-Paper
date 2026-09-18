from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class SelectionConfig:
    lambda_separability: float = 1.0
    lambda_anchor: float = 0.0
    robust_clip: float = 3.0
    scale_epsilon: float = 1e-12
    margin_weight: float = 0.5
    probability_weight: float = 0.5


def robust_unit(values, *, clip: float = 3.0, epsilon: float = 1e-12) -> np.ndarray:
    """Map values to [0,1] using median/MAD z-scores with documented fallbacks."""
    x = np.asarray(values, dtype=float)
    center = float(np.nanmedian(x))
    scale = 1.4826 * float(np.nanmedian(np.abs(x - center)))
    if not np.isfinite(scale) or scale <= epsilon:
        q25, q75 = np.nanpercentile(x, [25, 75])
        scale = float((q75 - q25) / 1.349)
    if not np.isfinite(scale) or scale <= epsilon:
        return np.full(x.shape, 0.5, dtype=float)
    z = np.clip((x - center) / scale, -clip, clip)
    return (z + clip) / (2.0 * clip)


def fit_mixed_transform(real: pd.DataFrame, numerical: list[str], categorical: list[str]):
    transformer = ColumnTransformer([
        ("numeric", StandardScaler(), numerical),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
    ], remainder="drop", sparse_threshold=0.0)
    transformer.fit(real[numerical + categorical])
    return transformer


def score_candidates(
    candidates: pd.DataFrame,
    real_train: pd.DataFrame,
    *,
    features: list[str],
    numerical: list[str],
    categorical: list[str],
    target: str,
    seed: int,
    config: SelectionConfig,
    anchor_score: np.ndarray | None = None,
) -> pd.DataFrame:
    transformer = fit_mixed_transform(real_train, numerical, categorical)
    real_x = np.asarray(transformer.transform(real_train[features]), dtype=float)
    candidate_x = np.asarray(transformer.transform(candidates[features]), dtype=float)
    real_y = real_train[target].to_numpy(dtype=int)
    candidate_y = candidates[target].to_numpy(dtype=int)

    nearest_real = NearestNeighbors(n_neighbors=1).fit(real_x)
    real_distance = nearest_real.kneighbors(candidate_x, return_distance=True)[0].ravel()
    hit = np.empty(len(candidates), dtype=float)
    miss = np.empty(len(candidates), dtype=float)
    for label in np.unique(candidate_y):
        index = np.flatnonzero(candidate_y == label)
        if not np.any(real_y == label) or not np.any(real_y != label):
            raise ValueError(f"Both real classes are required to score label {label}")
        hit_model = NearestNeighbors(n_neighbors=1).fit(real_x[real_y == label])
        miss_model = NearestNeighbors(n_neighbors=1).fit(real_x[real_y != label])
        hit[index] = hit_model.kneighbors(candidate_x[index], return_distance=True)[0].ravel()
        miss[index] = miss_model.kneighbors(candidate_x[index], return_distance=True)[0].ravel()

    classifier = RandomForestClassifier(
        n_estimators=300, min_samples_leaf=3, class_weight="balanced", random_state=seed, n_jobs=1
    ).fit(real_x, real_y)
    probabilities = classifier.predict_proba(candidate_x)
    class_columns = {int(label): i for i, label in enumerate(classifier.classes_)}
    confidence = np.asarray([probabilities[i, class_columns[int(label)]] for i, label in enumerate(candidate_y)])

    output = candidates.reset_index(drop=True).copy()
    output["candidate_index"] = np.arange(len(output), dtype=int)
    output["nearest_real_distance"] = real_distance
    output["nearest_hit_distance"] = hit
    output["nearest_miss_distance"] = miss
    output["margin_raw"] = miss - hit
    output["probability_raw"] = confidence
    output["realism"] = 1.0 - robust_unit(real_distance, clip=config.robust_clip, epsilon=config.scale_epsilon)
    output["margin"] = robust_unit(output["margin_raw"], clip=config.robust_clip, epsilon=config.scale_epsilon)
    output["probability"] = robust_unit(confidence, clip=config.robust_clip, epsilon=config.scale_epsilon)
    output["separability"] = config.margin_weight * output["margin"] + config.probability_weight * output["probability"]
    if anchor_score is None:
        output["anchor"] = 0.0
    else:
        output["anchor"] = robust_unit(anchor_score, clip=config.robust_clip, epsilon=config.scale_epsilon)
    output["score"] = output["realism"] + config.lambda_separability * output["separability"] + config.lambda_anchor * output["anchor"]
    return output


def select_by_quota(scored: pd.DataFrame, target: str, quotas: dict[int, int]) -> pd.DataFrame:
    selected = []
    for label, quota in sorted(quotas.items()):
        available = scored.loc[scored[target].eq(label)].copy()
        if len(available) < quota:
            raise RuntimeError(f"Candidate shortfall for class {label}: requested {quota}, available {len(available)}")
        chosen = available.sort_values(["score", "candidate_index"], ascending=[False, True], kind="mergesort").head(quota)
        selected.append(chosen)
    return pd.concat(selected, ignore_index=True)
