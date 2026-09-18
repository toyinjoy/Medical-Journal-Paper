# SepAware research repository

This repository supports the manuscript **“Separability-Aware Synthetic Data Selection for Rare-Outcome Prediction in Health Data.”** It contains the LaTeX source, reproducible experiment code, a frozen four-task manifest, fold-level outputs, statistical analyses, tables, figures, and research audits.

The outcome tasks are Vigitel obesity, COVID-19 hospital mortality, Vigitel current smoking, and kidney-cohort 365-day mortality. The two Vigitel tasks share one surveillance source and are not treated as independent cohorts. Dialysis is not an outcome in this study.

## Reproduction

Use Python 3.12 and follow [code/README.md](code/README.md). The full workflow is:

```sh
export SEPAWARE_DATA_ROOT=/authorized/data/directory
python code/scripts/reproduce_all.py --config code/configs/experiment_manifest.yaml
```

The command validates source hashes and schemas, runs tests, executes augmentation and TSTR experiments, regenerates corrected statistics, and rebuilds tables and figures. Source datasets are private or externally managed and are not committed. Expected file names, hashes, schemas, features, exclusions, and class counts are recorded in `code/configs/experiment_manifest.yaml`.

For a short integrity check:

```sh
export SEPAWARE_DATA_ROOT=/authorized/data/directory
python code/scripts/reproduce_all.py --smoke
```

Smoke outputs go to `/tmp` and are never manuscript evidence.

## Evidence map

- `results/raw/`: authoritative fold-level augmentation and TSTR outputs.
- `results/statistical_tests/`: corrected primary contrasts, multiplicity adjustment, sensitivity analyses, and factorial effects.
- `results/tables/`: generated aggregate tables.
- `results/experiment_coverage.csv`: machine-readable task-by-experiment status.
- `docs/research_audit.md`: pre-change repository and evidence audit.
- `docs/cross_task_experiment_matrix.md`: human-readable coverage matrix.
- `docs/reviewer_audit.md`: post-revision reviewer-style audit.
- `CHANGELOG.md`: scientific and editorial changes.
- `MANUSCRIPT_UNRESOLVED_COMMENTS.md`: author decisions that cannot be inferred from data.

TSTR and real-plus-synthetic augmentation answer different questions and are not pooled. Fixed-lambda tuning is exploratory because settings were compared on reporting folds. Clinical-anchor analyses remain dataset-specific and do not substitute for the common benchmark.

## Manuscript

Compile from the repository root:

```sh
tectonic main.tex
```

The final verified PDF is placed in `output/pdf/`. Ethics identifiers, funding, competing interests, CRediT roles, data-access wording, and a permanent repository license/URL require author confirmation before journal submission; they are not guessed in the manuscript.
