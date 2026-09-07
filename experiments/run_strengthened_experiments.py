#!/usr/bin/env python3
"""Strengthened two-dataset SepAware experiment.

The script keeps learned preprocessing inside each training fold, shares each
generator candidate pool between its standard and SepAware conditions, and
exports fold-level results for manuscript tables and figures.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import parallel_backend
from catboost import CatBoostClassifier
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler
from scipy.special import expit, logit
from scipy.spatial.distance import pdist
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sdv.metadata import SingleTableMetadata
from sdv.sampling import Condition
from sdv.single_table import CTGANSynthesizer, TVAESynthesizer


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "JMIR_SepAware" / "experiments" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


COVID_FEATURES = [
    "idade", "sexo", "etilismo", "tabagismo", "motivo_cancer", "motivo_msk",
    "motivo_digestivo2", "motivo_cardio2", "motivo_procedimentos2", "motivo_lesao2",
    "motivo_respiratorio", "motivo_neuro", "motivo_pele", "motivo_genitourinaria",
    "motivo_dm", "motivo_mental_subst", "motivo_infec2", "motivo_propedeutica",
    "n_comorbidades", "comorb_hipertensao", "comorb_ic", "comorb_dac",
    "comorb_fibrilacao", "comorb_avc", "comorb_dpoc", "comorb_asma", "comorb_dm",
    "comorb_obesidade", "comorb_drc", "comorb_cancer", "comorb_reumatologica",
    "comorb_cirrose", "comorb_hiv",
]

VIGITEL_FEATURES = [
    "age", "sex", "fumante", "exfuma", "inativo", "ativo_livre", "ati_livre",
    "diab", "hart", "dislipidemia", "doces5", "lanche_7", "gordura", "flvreg",
    "years_schooling",
]


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    path: Path
    target: str
    target_candidates: tuple[str, ...]
    features: tuple[str, ...]
    sample_n: int | None


SPECS = {
    "covid": DatasetSpec("COVID-19", ROOT / "banco_covidIH.xlsx", "obito", ("obito",), tuple(COVID_FEATURES), None),
    "vigitel": DatasetSpec(
        "Vigitel", ROOT / "vigitel2006_2023_obesidade_exclusoes.parquet", "obesity",
        ("obesity", "desfecho", "obesidade", "obeso"), tuple(VIGITEL_FEATURES), 5000,
    ),
}


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def _sex_binary(value):
    if pd.isna(value):
        return np.nan
    token = str(value).strip().lower()
    if token in {"f", "fem", "feminino", "female", "mulher", "woman", "2"}:
        return 1
    if token in {"m", "masc", "masculino", "male", "homem", "man", "1"}:
        return 0
    try:
        number = float(token)
        return int(number) if number in {0, 1} else np.nan
    except ValueError:
        return np.nan


def _binary_12(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    values = set(numeric.dropna().unique())
    if values and values.issubset({1, 2}):
        return numeric.map({1: 0, 2: 1})
    return numeric


def load_dataset(key: str, seed: int = 42) -> tuple[pd.DataFrame, list[str], str]:
    spec = SPECS[key]
    frame = pd.read_excel(spec.path) if spec.path.suffix == ".xlsx" else pd.read_parquet(spec.path)
    found = next((candidate for candidate in spec.target_candidates if candidate in frame.columns), None)
    if found is None:
        raise KeyError(f"Target not found for {key}: {spec.target_candidates}")
    if found != spec.target:
        frame = frame.rename(columns={found: spec.target})
    features = [name for name in spec.features if name in frame.columns]
    frame = frame[features + [spec.target]].copy()
    for sex in ("sex", "sexo"):
        if sex in frame and not pd.api.types.is_numeric_dtype(frame[sex]):
            frame[sex] = frame[sex].map(_sex_binary)
    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame[spec.target] = _binary_12(frame[spec.target]).round()
    frame = frame.dropna(subset=[spec.target])
    frame[spec.target] = frame[spec.target].clip(0, 1).astype(int)
    for column in features:
        values = set(frame[column].dropna().unique())
        if values and values.issubset({1, 2}):
            frame[column] = _binary_12(frame[column])
    if spec.sample_n and len(frame) > spec.sample_n:
        parts = []
        for cls, group in frame.groupby(spec.target):
            take = int(round(spec.sample_n * len(group) / len(frame)))
            parts.append(group.sample(n=min(len(group), max(1, take)), random_state=seed + int(cls)))
        frame = pd.concat(parts).sample(frac=1, random_state=seed).head(spec.sample_n).reset_index(drop=True)
    return frame.reset_index(drop=True), features, spec.target


def fit_fold_imputer(train: pd.DataFrame, features: list[str]) -> tuple[SimpleImputer, list[str]]:
    imputer = SimpleImputer(strategy="median")
    imputer.fit(train[features])
    return imputer, features


def impute_frame(frame: pd.DataFrame, imputer: SimpleImputer, features: list[str], target: str) -> pd.DataFrame:
    output = pd.DataFrame(imputer.transform(frame[features]), columns=features, index=frame.index)
    for column in features:
        source_unique = frame[column].dropna().nunique()
        if source_unique <= 2:
            output[column] = output[column].round().clip(0, 1).astype(int)
    output[target] = frame[target].to_numpy(dtype=int)
    return output.reset_index(drop=True)


def make_models(seed: int, weighted: bool = False):
    weight = "balanced" if weighted else None
    return {
        "LogisticRegression": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, class_weight=weight, random_state=seed)),
        ]),
        "RandomForest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, class_weight=weight, random_state=seed, n_jobs=-1
        ),
        "CatBoost": CatBoostClassifier(
            iterations=300, depth=4, learning_rate=0.05, loss_function="Logloss",
            random_seed=seed, verbose=False, allow_writing_files=False,
            auto_class_weights="Balanced" if weighted else None,
        ),
    }


def calibration_parameters(y: np.ndarray, probability: np.ndarray) -> tuple[float, float]:
    clipped = np.clip(probability, 1e-6, 1 - 1e-6)
    predictor = logit(clipped).reshape(-1, 1)
    try:
        model = LogisticRegression(C=1e6, max_iter=2000).fit(predictor, y)
        return float(model.intercept_[0]), float(model.coef_[0, 0])
    except Exception:
        return np.nan, np.nan


def predictive_metrics(y: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    prediction = (probability >= 0.5).astype(int)
    intercept, slope = calibration_parameters(y, probability)
    return {
        "macro_f1": f1_score(y, prediction, average="macro", zero_division=0),
        "minority_f1": f1_score(y, prediction, pos_label=1, zero_division=0),
        "minority_precision": precision_score(y, prediction, pos_label=1, zero_division=0),
        "minority_recall": recall_score(y, prediction, pos_label=1, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y, prediction),
        "auprc": average_precision_score(y, probability),
        "auroc": roc_auc_score(y, probability) if len(np.unique(y)) == 2 else np.nan,
        "brier": brier_score_loss(y, probability),
        "calibration_intercept": intercept,
        "calibration_slope": slope,
    }


def fit_evaluate(train: pd.DataFrame, test: pd.DataFrame, features: list[str], target: str, seed: int, weighted=False):
    rows = []
    for name, model in make_models(seed, weighted).items():
        fitted = clone(model).fit(train[features], train[target])
        probability = fitted.predict_proba(test[features])[:, 1]
        rows.append({"classifier": name, **predictive_metrics(test[target].to_numpy(), probability)})
    return rows


def sdv_metadata(frame: pd.DataFrame, features: list[str], target: str) -> SingleTableMetadata:
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(frame[features + [target]])
    metadata.update_column(column_name=target, sdtype="categorical")
    for column in features:
        if frame[column].nunique(dropna=True) <= 10 and np.allclose(frame[column], frame[column].round()):
            metadata.update_column(column_name=column, sdtype="categorical")
    return metadata


def train_generator(kind: str, frame: pd.DataFrame, features: list[str], target: str, epochs: int, seed: int):
    seed_everything(seed)
    metadata = sdv_metadata(frame, features, target)
    cls = CTGANSynthesizer if kind == "CTGAN" else TVAESynthesizer
    synthesizer = cls(metadata, epochs=epochs, verbose=False, cuda=False)
    with parallel_backend("threading", n_jobs=1):
        synthesizer.fit(frame[features + [target]])
    return synthesizer


def train_minority_generator(kind: str, frame: pd.DataFrame, features: list[str], epochs: int, seed: int):
    """Fit a class-conditional feature generator when outcome rejection fails."""
    seed_everything(seed)
    minority = frame.loc[frame.iloc[:, -1] == 1, features].copy()
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(minority)
    for column in features:
        if minority[column].nunique(dropna=True) <= 10 and np.allclose(minority[column], minority[column].round()):
            metadata.update_column(column_name=column, sdtype="categorical")
    cls = CTGANSynthesizer if kind == "CTGAN" else TVAESynthesizer
    synthesizer = cls(metadata, epochs=epochs, verbose=False, cuda=False)
    with parallel_backend("threading", n_jobs=1):
        synthesizer.fit(minority)
    return synthesizer


def clean_generated(frame: pd.DataFrame, reference: pd.DataFrame, features: list[str], target: str) -> pd.DataFrame:
    output = frame[features + [target]].copy()
    for column in features:
        output[column] = pd.to_numeric(output[column], errors="coerce").fillna(reference[column].median())
        if reference[column].nunique() <= 2:
            output[column] = output[column].round().clip(0, 1).astype(int)
        else:
            output[column] = output[column].clip(reference[column].min(), reference[column].max())
    output[target] = pd.to_numeric(output[target], errors="coerce").fillna(0).round().clip(0, 1).astype(int)
    return output.reset_index(drop=True)


def candidate_pool(synthesizer, needed: int, reference: pd.DataFrame, features: list[str], target: str, multiplier: int):
    # Conditional sampling makes the augmentation target explicit and avoids
    # turning a generator's unconditional class prevalence into an accidental
    # additional treatment. Standard and SepAware conditions share this pool.
    total = max(needed * multiplier, needed)
    condition = Condition({target: 1}, num_rows=total)
    generated = synthesizer.sample_from_conditions(
        conditions=[condition], max_tries_per_batch=500, batch_size=max(100, total)
    )
    return clean_generated(generated, reference, features, target)


def minority_candidate_pool(synthesizer, needed: int, reference: pd.DataFrame, features: list[str], target: str, multiplier: int):
    total = max(needed * multiplier, needed)
    generated = synthesizer.sample(num_rows=total)
    generated[target] = 1
    return clean_generated(generated, reference, features, target)


def score_candidates(pool: pd.DataFrame, real_train: pd.DataFrame, features: list[str], target: str, seed: int):
    scaler = StandardScaler().fit(real_train[features])
    real_x = scaler.transform(real_train[features])
    candidate_x = scaler.transform(pool[features])
    real_y = real_train[target].to_numpy(dtype=int)
    candidate_y = pool[target].to_numpy(dtype=int)
    nn_all = NearestNeighbors(n_neighbors=1).fit(real_x)
    realism_distance = nn_all.kneighbors(candidate_x, return_distance=True)[0].ravel()
    same_distance = np.zeros(len(pool))
    opposite_distance = np.zeros(len(pool))
    for cls in (0, 1):
        idx = np.flatnonzero(candidate_y == cls)
        if not len(idx):
            continue
        same = NearestNeighbors(n_neighbors=1).fit(real_x[real_y == cls])
        opposite = NearestNeighbors(n_neighbors=1).fit(real_x[real_y != cls])
        same_distance[idx] = same.kneighbors(candidate_x[idx], return_distance=True)[0].ravel()
        opposite_distance[idx] = opposite.kneighbors(candidate_x[idx], return_distance=True)[0].ravel()
    boundary = RandomForestClassifier(
        n_estimators=300, min_samples_leaf=3, class_weight="balanced", random_state=seed, n_jobs=-1
    ).fit(real_train[features], real_y)
    probability = boundary.predict_proba(pool[features])
    confidence = probability[np.arange(len(pool)), candidate_y]

    def normalize(values):
        values = np.asarray(values, dtype=float)
        low, high = np.nanmin(values), np.nanmax(values)
        return np.full(len(values), 0.5) if not np.isfinite(high - low) or high == low else (values - low) / (high - low)

    scored = pool.copy()
    scored["realism"] = 1 - normalize(realism_distance)
    scored["margin"] = opposite_distance - same_distance
    scored["separability"] = 0.5 * normalize(scored["margin"]) + 0.5 * normalize(confidence)
    scored["score"] = scored["realism"] + scored["separability"]
    return scored


def augment_minority(real_train: pd.DataFrame, selected: pd.DataFrame, features: list[str], target: str):
    clean = selected[features + [target]].copy()
    clean[target] = 1
    return pd.concat([real_train[features + [target]], clean], ignore_index=True)


def structure_privacy_metrics(real_train, real_test, synthetic, features, target):
    syn_min = synthetic[synthetic[target] == 1]
    test_min = real_test[real_test[target] == 1]
    if syn_min.empty or test_min.empty:
        return {name: np.nan for name in ["minority_coverage_distance", "minority_diversity", "exact_match_rate", "membership_auc"]}
    scaler = StandardScaler().fit(real_train[features])
    train_x = scaler.transform(real_train[features])
    test_x = scaler.transform(real_test[features])
    syn_x = scaler.transform(synthetic[features])
    syn_min_x = scaler.transform(syn_min[features])
    test_min_x = scaler.transform(test_min[features])
    coverage = NearestNeighbors(n_neighbors=1).fit(syn_min_x).kneighbors(test_min_x, return_distance=True)[0].mean()
    sample = syn_min_x[: min(1000, len(syn_min_x))]
    diversity = float(np.mean(pdist(sample))) if len(sample) > 1 else 0.0
    nearest_real = NearestNeighbors(n_neighbors=1).fit(train_x).kneighbors(syn_x, return_distance=True)[0].ravel()
    exact = float(np.mean(nearest_real < 1e-10))
    nn_syn = NearestNeighbors(n_neighbors=1).fit(syn_x)
    member_dist = nn_syn.kneighbors(train_x, return_distance=True)[0].ravel()
    nonmember_dist = nn_syn.kneighbors(test_x, return_distance=True)[0].ravel()
    labels = np.r_[np.ones(len(member_dist)), np.zeros(len(nonmember_dist))]
    scores = -np.r_[member_dist, nonmember_dist]
    membership = roc_auc_score(labels, scores)
    return {
        "minority_coverage_distance": float(coverage),
        "minority_diversity": diversity,
        "exact_match_rate": exact,
        "membership_auc": float(membership),
    }


def run_dataset(key: str, splits: int, repeats: int, epochs: int, pool_multiplier: int, generators: list[str], seed: int):
    raw, features, target = load_dataset(key, seed)
    splitter = RepeatedStratifiedKFold(n_splits=splits, n_repeats=repeats, random_state=seed)
    prediction_rows, diagnostic_rows = [], []
    for split_index, (train_idx, test_idx) in enumerate(splitter.split(raw, raw[target])):
        repeat = split_index // splits
        fold = split_index % splits
        fold_seed = seed + repeat * 1000 + fold * 37
        raw_train, raw_test = raw.iloc[train_idx].copy(), raw.iloc[test_idx].copy()
        imputer, _ = fit_fold_imputer(raw_train, features)
        train = impute_frame(raw_train, imputer, features, target)
        test = impute_frame(raw_test, imputer, features, target)
        n_add = max(0, int((train[target] == 0).sum() - (train[target] == 1).sum()))

        datasets = {"Real only": (train, False), "Class weighting": (train, True)}
        x, y = train[features], train[target]
        for name, sampler in {
            "Random oversampling": RandomOverSampler(random_state=fold_seed),
            "Random undersampling": RandomUnderSampler(random_state=fold_seed),
            "SMOTE": SMOTE(random_state=fold_seed, k_neighbors=max(1, min(5, int((y == 1).sum()) - 1))),
        }.items():
            rx, ry = sampler.fit_resample(x, y)
            sampled = pd.DataFrame(rx, columns=features)
            sampled[target] = np.asarray(ry, dtype=int)
            datasets[name] = (sampled, False)

        for generator_index, generator in enumerate(generators):
            generator_seed = fold_seed + 10000 * (generator_index + 1)
            started = time.time()
            if generator == "TVAE":
                # SDV 1.17 explicitly does not implement native conditional
                # sampling for TVAE. Fit the minority conditional directly.
                synth = train_minority_generator(generator, train, features, epochs, generator_seed)
                pool = minority_candidate_pool(synth, n_add, train, features, target, pool_multiplier)
                sampling_strategy = "minority-conditional TVAE"
            else:
                synth = train_generator(generator, train, features, target, epochs, generator_seed)
                pool = candidate_pool(synth, n_add, train, features, target, pool_multiplier)
                sampling_strategy = "outcome-conditional rejection sampling"
            positives = pool[pool[target] == 1].copy()
            if len(positives) < n_add:
                raise RuntimeError(f"{generator} produced {len(positives)} positives; {n_add} required")
            standard = positives.sample(n=n_add, random_state=generator_seed)
            scored = score_candidates(pool, train, features, target, generator_seed)
            selected = scored[scored[target] == 1].nlargest(n_add, "score")
            datasets[f"Standard {generator}"] = (augment_minority(train, standard, features, target), False)
            datasets[f"SepAware {generator}"] = (augment_minority(train, selected, features, target), False)
            for condition, selected_syn in [(f"Standard {generator}", standard), (f"SepAware {generator}", selected)]:
                diagnostic_rows.append({
                    "dataset": SPECS[key].name, "repeat": repeat, "fold": fold, "condition": condition,
                    "generator_seed": generator_seed, "generator_seconds": time.time() - started,
                    "sampling_strategy": sampling_strategy,
                    **structure_privacy_metrics(train, test, selected_syn, features, target),
                })

        for condition, (training, weighted) in datasets.items():
            for row in fit_evaluate(training, test, features, target, fold_seed, weighted=weighted):
                prediction_rows.append({
                    "dataset": SPECS[key].name, "repeat": repeat, "fold": fold,
                    "partition_seed": seed + repeat, "fold_seed": fold_seed,
                    "condition": condition, "n_train": len(training), "n_test": len(test),
                    "positive_rate_train": float(training[target].mean()),
                    "positive_rate_test": float(test[target].mean()), **row,
                })
        pd.DataFrame(prediction_rows).to_csv(OUT / "predictive_metrics_checkpoint.csv", index=False)
        pd.DataFrame(diagnostic_rows).to_csv(OUT / "synthetic_diagnostics_checkpoint.csv", index=False)
        print(json.dumps({"dataset": key, "repeat": repeat, "fold": fold, "conditions": len(datasets)}), flush=True)
    return prediction_rows, diagnostic_rows


def summarize(frame: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    grouped = frame.groupby(["dataset", "condition", "classifier"], dropna=False)
    rows = []
    for keys, group in grouped:
        row = dict(zip(["dataset", "condition", "classifier"], keys))
        row["n"] = len(group)
        for metric in metrics:
            values = group[metric].dropna().to_numpy(float)
            row[f"{metric}_mean"] = float(np.mean(values)) if len(values) else np.nan
            row[f"{metric}_sd"] = float(np.std(values, ddof=1)) if len(values) > 1 else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--datasets", nargs="+", choices=list(SPECS), default=list(SPECS))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--splits", type=int)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--epochs", type=int)
    args = parser.parse_args()
    if args.mode == "smoke":
        splits, repeats, epochs, multiplier, generators = 2, 1, 2, 2, ["TVAE"]
    else:
        splits, repeats, epochs, multiplier, generators = 5, 3, 100, 5, ["CTGAN", "TVAE"]
    splits = args.splits or splits
    repeats = args.repeats or repeats
    epochs = args.epochs or epochs
    config = vars(args) | {"splits": splits, "repeats": repeats, "epochs": epochs, "pool_multiplier": multiplier, "generators": generators}
    (OUT / "run_config.json").write_text(json.dumps(config, indent=2))
    prediction_rows, diagnostic_rows = [], []
    for dataset in args.datasets:
        pred, diag = run_dataset(dataset, splits, repeats, epochs, multiplier, generators, args.seed)
        prediction_rows.extend(pred)
        diagnostic_rows.extend(diag)
    predictions = pd.DataFrame(prediction_rows)
    diagnostics = pd.DataFrame(diagnostic_rows)
    predictions.to_csv(OUT / "predictive_metrics_long.csv", index=False)
    diagnostics.to_csv(OUT / "synthetic_diagnostics_long.csv", index=False)
    summarize(predictions, ["auprc", "macro_f1", "minority_f1", "minority_recall", "auroc", "brier"]).to_csv(
        OUT / "predictive_metrics_summary.csv", index=False
    )
    print(f"Wrote results to {OUT}")


if __name__ == "__main__":
    main()
