from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def _binary(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    values = set(numeric.dropna().unique())
    return numeric.map({1: 0, 2: 1}) if values and values <= {1, 2} else numeric


def kidney_landmark(path: Path) -> pd.DataFrame:
    events = pd.read_feather(path, columns=["date", "patient_id", "event"])
    events["date"] = pd.to_datetime(events["date"])
    spans = events.groupby("patient_id")["date"].agg(first_date="min", last_date="max")
    spans["index_date"] = spans.first_date + pd.Timedelta(days=365)
    spans["horizon_end"] = spans.index_date + pd.Timedelta(days=365)
    deaths = events.loc[events.event.eq("DEATH")].groupby("patient_id").date.min().rename("death_date")
    spans = spans.join(deaths)
    spans["death_365d"] = spans.death_date.gt(spans.index_date) & spans.death_date.le(spans.horizon_end)
    eligible = (spans.last_date.ge(spans.horizon_end) | spans.death_365d) & (spans.death_date.isna() | spans.death_date.gt(spans.index_date))
    spans = spans.loc[eligible]
    base = events.merge(spans[["index_date"]], left_on="patient_id", right_index=True)
    base = base.loc[base.date.lt(base.index_date) & ~base.event.eq("DEATH")].copy()
    code = base.event.astype(str)
    masks = {
        "diagnosis_count": code.str.startswith("DIAGN_"), "medication_count": code.str.contains("MED_", regex=False),
        "dialysis_hd_count": code.eq("EVENT_C1DIALISE_HD"), "dialysis_dp_count": code.eq("EVENT_C1DIALISE_DP"),
        "diag_n180_count": code.eq("DIAGN_N180"), "diag_n189_count": code.eq("DIAGN_N189"), "diag_n188_count": code.eq("DIAGN_N188"),
        "transplant_z940_count": code.eq("DIAGN_Z940"), "transplant_event_count": code.str.contains("TX_", regex=False),
        "vascular_access_count": code.str.contains("ACESSO_", regex=False), "hospitalization_count": code.str.contains("INTERNA", regex=False),
        "erythropoietin_count": code.eq("EVENT_c2MED_ERITRO"),
    }
    parts = [base.groupby("patient_id").size().rename("baseline_event_count"), base.groupby("patient_id").event.nunique().rename("baseline_unique_event_count"), base.groupby("patient_id").date.nunique().rename("baseline_active_days")]
    parts += [mask.groupby(base.patient_id).sum().rename(name) for name, mask in masks.items()]
    cohort = pd.concat(parts, axis=1).reindex(spans.index).fillna(0)
    cohort["death_365d"] = spans.death_365d.astype(int)
    cohort["patient_id"] = cohort.index
    return cohort.reset_index(drop=True)


def load_task(task_key: str, task: dict, root: Path, sample_seed: int = 42) -> pd.DataFrame:
    path = root / task["path"]
    loader = task["loader"]
    if loader == "excel": frame = pd.read_excel(path)
    elif loader == "parquet": frame = pd.read_parquet(path)
    elif loader == "pickle": frame = pd.DataFrame(pd.read_pickle(path))
    elif loader == "kidney_landmark": frame = kidney_landmark(path)
    else: raise ValueError(loader)
    target, features = task["outcome"], task["features"]
    keep = features + [target] + ([task["group_column"]] if task.get("group_column") and task["group_column"] in frame else [])
    frame = frame[keep].copy()
    if "sexo" in frame and not pd.api.types.is_numeric_dtype(frame.sexo):
        frame["sexo"] = frame.sexo.astype(str).str.lower().map({"m": 0, "masculino": 0, "1": 0, "f": 1, "feminino": 1, "2": 1})
    for column in features + [target]: frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame[target] = _binary(frame[target]).round()
    frame = frame.dropna(subset=[target]); frame[target] = frame[target].astype(int)
    for column in task["categorical"]: frame[column] = _binary(frame[column])
    n = task.get("sample_n")
    if n and len(frame) > n:
        pieces=[]
        for label, group in frame.groupby(target):
            take=round(n*len(group)/len(frame)); pieces.append(group.sample(n=int(take), random_state=sample_seed+int(label)))
        frame=pd.concat(pieces).sample(frac=1, random_state=sample_seed).head(n)
    return frame.reset_index(drop=True)
