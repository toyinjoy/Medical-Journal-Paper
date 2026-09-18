# Reviewer-style audit

Date: 2026-09-17  
Scope: revised manuscript and authoritative repository outputs

## Reviewer 1: biomedical-informatics methodology

| Severity | Concern and location | Required action | Resolution | Evidence / remaining limitation |
|---|---|---|---|---|
| Major | Abstract, Results, Discussion: generator-relative gains could be read as superiority over clinical baselines | Put conventional baselines first and state whether selected generators beat them | Resolved | `results/tables/common_benchmark_primary.csv`; none of the selected generators led AUPRC |
| Major | Methods: Vigitel obesity and smoking could be presented as independent validation cohorts | State their shared source wherever task breadth is interpreted | Resolved | Methods dataset section; Results overview; Discussion |
| Major | Methods/Results: anchor experiments were absent for two tasks | Do not invent post-hoc anchors; separate task-specific analyses | Resolved | Manifest `non_applicable`; dataset-specific Results subsection |
| Major | Generalizability: all evidence is internal cross-validation | Remove clinical-benefit and external-validation implications | Resolved in wording; limitation remains | Limitations and Conclusion |
| Minor | Kidney outcome construction needs clinical review | Preserve exact landmark definition and request data-custodian review | Partly resolved | Manifest and Methods define it; clinical validation remains outstanding |

## Reviewer 2: statistics and machine learning

| Severity | Concern and location | Required action | Resolution | Evidence / remaining limitation |
|---|---|---|---|---|
| Major | Legacy paired intervals treated 45 fold--classifier values as independent | Average classifiers within folds and use repeated-CV correction | Resolved | `code/src/sepaware/statistics.py`; `results/statistical_tests/primary_contrasts.csv` |
| Major | Eight primary task--generator tests lacked multiplicity correction | Apply prespecified Holm adjustment | Resolved | `multiplicity_adjusted_results.csv` |
| Major | Split/preprocessing/generation leakage risk | Split first; fit all transformations and generators on real training folds; add tests | Resolved | experiment scripts; `code/tests/test_no_leakage.py` |
| Major | Reporting-fold lambda selection | Exclude grid from confirmatory claims | Resolved | Methods and supplement identify it as exploratory/superseded |
| Major | Factorial reporting emphasized ANOVA percentages without effects and intervals | Export fold-paired effects and confidence intervals | Resolved | `results/statistical_tests/factorial_effects.csv` |
| Minor | Threshold-dependent recall could conflict with AUPRC | State fixed threshold and report Brier/calibration separately | Resolved | Methods and Results |
| Minor | Corrected repeated-CV procedure is approximate | State dependence assumptions and avoid equivalence claims | Resolved in wording; limitation remains | Supplement statistical method; Discussion |

## Reviewer 3: synthetic health data and privacy

| Severity | Concern and location | Required action | Resolution | Evidence / remaining limitation |
|---|---|---|---|---|
| Major | Fidelity was absent from the four-task outputs | Run common marginal, correlation, and detection diagnostics | Resolved when final TSTR exports complete | `results/raw/tstr_diagnostics.csv`; generated diagnostic summary |
| Major | Improved separability may result from prototype concentration | Report positive-class coverage and diversity together | Resolved | augmentation and TSTR diagnostic outputs; Results and Discussion |
| Major | Exact matches and a nearest-distance membership proxy do not prove privacy | Remove anonymity claims and define the attacker limitation | Resolved | Methods, Results, Discussion |
| Major | TVAE generation is asymmetric with CTGAN | Document class-specific TVAE fitting and avoid generator-agnostic claims | Resolved | Methods and Limitations |
| Minor | Attribute/linkage attacks and formal privacy guarantees are absent | Retain as an explicit limitation; do not release synthetic records on current evidence | Unresolved by available experiments | Limitations; no attribute-inference implementation or threat model |

## Second-revision actions

The second pass made the following changes in response to this audit:

1. Reordered Results so the common benchmark and conventional baselines precede generator comparisons and dataset-specific analyses.
2. Replaced naive intervals with corrected paired contrasts and Holm-adjusted results.
3. Added the implementable selection equations, deterministic tie-breaking, shortfall behavior, and fold-contained Algorithm 1.
4. Separated augmentation from TSTR and excluded dataset-specific anchors from cross-task averages.
5. Rewrote the Discussion around null results, conventional comparators, source dependence, diversity loss, threshold choice, and privacy limits.
6. Added explicit declaration text for facts unavailable in the repository rather than inventing ethics, funding, or access statements.

## Submission-blocking author information

The analyses can be made reproducible from authorized data, but journal submission remains blocked until the author supplies ethics/waiver identifiers, funding, competing interests, CRediT roles, institutional data-provenance wording, and a repository license/permanent URL. These are factual governance statements and cannot be derived from the datasets.
