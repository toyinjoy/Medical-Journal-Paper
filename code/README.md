# Reproducing the SepAware study

## Study and structure

The code evaluates post-generation candidate selection for four binary outcome tasks. The two Vigitel tasks share one surveillance source and are never treated as independent external cohorts.

- `configs/experiment_manifest.yaml`: frozen task definitions, source hashes, features, seeds and settings.
- `src/sepaware/`: importable data, selection, evaluation, diagnostics and statistics logic.
- `scripts/`: validation, experiment and reporting entry points.
- `tests/`: unit and leakage-control tests.
- `../results/raw/`: fold-level authoritative outputs.
- `../results/statistical_tests/`: regenerated inferential results.

## Environment

Python 3.12 is required. From the repository root:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -e 'code[test]'
```

Exact direct dependency versions are in `pyproject.toml`. Experiments were run on CPU. A full run is expected to take several hours, depending on CPU and SDV performance.

## Authorized data placement

The source datasets are not committed. Set `SEPAWARE_DATA_ROOT` to a directory containing:

```text
banco_covidIH.xlsx
vigitel2006_2023_obesidade_exclusoes.parquet
Vigitel_Dataset/samples.pkl
tidy_event_data.feather
```

The manifest records SHA-1 hashes, schemas, outcomes, exclusions and expected analytic counts. Validation fails on a missing or changed source rather than silently using it.

```sh
export SEPAWARE_DATA_ROOT=/authorized/data/directory
.venv/bin/python code/scripts/validate_data.py
```

No credentials, source patient records or absolute local data paths should be committed.

## Tests and smoke checks

```sh
PYTHONPATH=code/src .venv/bin/python -m pytest code/tests -q
SEPAWARE_DATA_ROOT=/authorized/data/directory PYTHONPATH=code/src \
  .venv/bin/python experiments/run_strengthened_experiments.py \
  --mode smoke --datasets covid --output-dir /tmp/sepaware-smoke
SEPAWARE_DATA_ROOT=/authorized/data/directory PYTHONPATH=code/src \
  .venv/bin/python code/scripts/run_tstr.py --tasks covid_mortality --smoke \
  --output-dir /tmp/sepaware-tstr-smoke
```

Smoke outputs are integrity checks and must not be copied into manuscript results.

## Full experiments

```sh
SEPAWARE_DATA_ROOT=/authorized/data/directory PYTHONPATH=code/src \
  .venv/bin/python experiments/run_strengthened_experiments.py \
  --mode full --epochs 30 --datasets covid vigitel vigitel_smoking kidney_mortality \
  --output-dir results/raw

SEPAWARE_DATA_ROOT=/authorized/data/directory PYTHONPATH=code/src \
  .venv/bin/python code/scripts/run_tstr.py

PYTHONPATH=code/src .venv/bin/python code/scripts/run_statistics.py
PYTHONPATH=code/src .venv/bin/python code/scripts/build_tables.py
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=code/src \
  .venv/bin/python code/scripts/build_figures.py
```

`reproduce_all.py` runs validation, tests, augmentation, TSTR and statistics in this order. It stops at the first failure.

## Seed policy

Partition seeds are 42, 43 and 44. Generator seeds are distinct by generator, repetition and fold. Classifier and resampling seeds are recorded at fold level. Standard and SepAware variants share a candidate pool. The held-out fold is never used for preprocessing, generation, scoring or threshold tuning.

## Known limitations

- TVAE lacks native conditional sampling in SDV 1.17.2; TSTR fits class-specific TVAE models and augmentation fits the positive-class model.
- The membership proxy is a nearest-synthetic diagnostic, not proof of anonymity.
- Internal repeated cross-validation is not external validation.
- The meaning of the nonunique Vigitel obesity source key requires data-owner confirmation; the analytic features do not include this key.
