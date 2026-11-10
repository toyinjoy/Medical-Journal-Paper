# SepAware CTGAN curation study

This repository supports the manuscript **“Separability-Aware Curation of Synthetic Health Data: Conditional Utility, Coverage, and Calibration in Minority-Class Prediction.”** The journal paper asks a deliberately narrow question: when the generator and candidate pool are fixed, can post-generation curation improve synthetic-to-real minority classification? CTGAN is therefore a controlled infrastructure component, not a model-comparison factor.

The outcome tasks are Vigitel obesity, COVID-19 hospital mortality, Vigitel current smoking, and kidney-cohort 365-day mortality. The two Vigitel tasks share one surveillance source and are not treated as independent cohorts. Dialysis is not an outcome in this study.

## Paper evidence

- `results/ctgan_locked/locked_summary.csv`: locked Standard CTGAN and SepAware metric means.
- `results/ctgan_locked/locked_inference.csv`: paired effects, group-bootstrap intervals, prediction-swap tests, and Holm adjustment.
- `results/ctgan_locked/mechanism_summary.csv`: candidate-pool coverage, selected-set overlap, and progressive-replacement evidence.
- `docs/PAPER_EVIDENCE_SCOPE.md`: boundary between active paper evidence and historical development runs.

The paper follows the **Generate--Curate--Decide** framework: CTGAN generates a shared candidate pool, SepAware curates a quota-matched training set, and downstream classifiers choose operating thresholds from synthetic training data only.

## Historical reproduction

The earlier multi-generator workflow is retained for provenance but is not part of the journal paper's active evidence chain. Use Python 3.12 and follow [code/README.md](code/README.md) to audit those historical runs:

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

## Repository map

- `results/ctgan_locked/`: active CTGAN-only paper evidence.
- `results/raw/`, `results/statistical_tests/`, and `results/tables/`: historical development evidence, excluded from current paper claims.
- `results/experiment_coverage.csv`: machine-readable task-by-experiment status.
- `docs/research_audit.md`: pre-change repository and evidence audit.
- `docs/cross_task_experiment_matrix.md`: human-readable coverage matrix.
- `docs/reviewer_audit.md`: post-revision reviewer-style audit.
- `CHANGELOG.md`: scientific and editorial changes.
- `MANUSCRIPT_UNRESOLVED_COMMENTS.md`: author decisions that cannot be inferred from data.

The paper reports TSTR only. Real-plus-synthetic augmentation, generator comparisons, reporting-fold tuning, and dataset-specific development studies are not pooled into the confirmatory claim.

## Manuscript

Compile from the repository root:

```sh
tectonic main.tex
tectonic supplement.tex
```

The main manuscript is capped at 15 pages; detailed algorithms and audit material are in the separate supplement. Ethics identifiers, funding, competing interests, CRediT roles, data-access wording, a citable reference for the preceding CTGAN development study, and a permanent repository license/URL require author confirmation before journal submission; they are not guessed in the manuscript.
