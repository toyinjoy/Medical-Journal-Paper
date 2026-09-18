# Completion report

Date: 2026-09-17

## What was rerun

- Source hash, schema, sample-size, and class-count validation for all four tasks.
- The full real-plus-synthetic augmentation benchmark: 4 tasks x 9 methods x 3 classifiers x 3 repetitions x 5 folds (1,620 rows), plus 240 generator-diagnostic rows.
- Standard and SepAware CTGAN and TVAE TSTR: 4 tasks x 4 conditions x 3 classifiers x 3 repetitions x 5 folds (720 rows), plus 240 fidelity/privacy/geometry rows.
- Nadeau--Bengio corrected primary AUPRC contrasts, Holm adjustment, classifier/repetition sensitivity, and fold-paired factorial effects.
- Table and figure generation, source consistency checks, five unit/leakage/reproducibility tests, and both augmentation and TSTR smoke workflows.

## Numerical changes

The authoritative rerun changed the SepAware-minus-standard CTGAN AUPRC differences previously present in the draft to 0.0122 (COVID-19), 0.0086 (Vigitel obesity), 0.0314 (Vigitel smoking), and 0.0053 (kidney mortality). Corrected 95% intervals include zero for COVID-19, obesity, and kidney mortality. Smoking is the only primary contrast that remains nonzero after Holm adjustment (95% CI 0.0149--0.0479; adjusted p=.0091). All four TVAE contrasts include zero.

In TSTR, CTGAN selection changed mean AUPRC from 0.2787 to 0.3330 (COVID-19), 0.1912 to 0.2792 (obesity), 0.1387 to 0.2789 (smoking), and 0.0628 to 0.0801 (kidney mortality). These substitution results are descriptive and separate from augmentation inference.

The TSTR privacy diagnostics identified a material adverse result not present in the prior draft: kidney TVAE exact-match rates were 0.1052 under standard sampling and 0.1342 after selection. Several detection AUROCs were near one. The manuscript now advises against release on this evidence.

## Manuscript claims changed

- Removed claims based on legacy point estimates and naive independent-fold intervals.
- Replaced broad CTGAN-improvement language with the corrected finding that only smoking had an adjusted primary gain.
- Stated that no selected generator led the conventional AUPRC comparison on any task.
- Separated TSTR from augmentation in Methods, Results, tables, and interpretation.
- Presented the two Vigitel outcomes as tasks from one source, not independent cohorts.
- Limited clinical-anchor evidence to the tasks with independently specified anchors.
- Added the diversity cost, kidney TVAE duplication risk, detection results, and privacy limitations.
- Replaced the high-level SepAware description with equations and pseudocode matching the implementation.

## Experiments not completed

All 84 scientifically transferable task--experiment cells in the declared matrix are complete. Attribute-inference attacks, shadow-model membership attacks, temporal/external validation, phenotype-defined coverage, higher-capacity generator sensitivity, and multiple generator seeds per fold were not part of the frozen common matrix and remain future work. The reporting-fold lambda grid is superseded, not confirmatory.

## Remaining reviewer and submission risks

- Ethics committee/IRB names and identifiers, consent or waiver determinations, and legal data-use wording are absent from the repository.
- Funding, competing interests, CRediT roles, full author metadata, a repository license, and a permanent archive URL require author confirmation.
- The meaning of the nonunique Vigitel obesity source key should be confirmed by the data owner before claiming participant-level independence.
- The kidney landmark/event definitions require clinical and data-custodian review.
- Internal repeated cross-validation does not establish external clinical validity.
- The membership proxy is not a formal privacy guarantee; kidney TVAE exact matches are a direct release concern.

## Exact reproduction commands

From the repository root with Python 3.12 dependencies installed:

```sh
export SEPAWARE_DATA_ROOT=/authorized/data/directory
PYTHONPATH=code/src python code/scripts/validate_data.py
PYTHONPATH=code/src python -m pytest code/tests -q
PYTHONPATH=code/src python experiments/run_strengthened_experiments.py --mode full --epochs 30 --datasets covid vigitel vigitel_smoking kidney_mortality --output-dir results/raw
PYTHONPATH=code/src python code/scripts/run_tstr.py --config code/configs/experiment_manifest.yaml
PYTHONPATH=code/src python code/scripts/run_statistics.py
PYTHONPATH=code/src python code/scripts/build_tables.py
MPLCONFIGDIR=/tmp/matplotlib PYTHONPATH=code/src python code/scripts/build_figures.py
PYTHONPATH=code/src python code/scripts/check_consistency.py
tectonic main.tex
```

The equivalent single experiment command is:

```sh
export SEPAWARE_DATA_ROOT=/authorized/data/directory
python code/scripts/reproduce_all.py --config code/configs/experiment_manifest.yaml
```
