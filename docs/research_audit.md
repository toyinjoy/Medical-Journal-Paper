# Research and evidence audit

Date: 2026-09-17  
Repository: `Medical-Journal-Paper`  
Audited commit: `b8b4276f478df8f1d87277833effe428cac0fac1`

## Executive assessment

The repository is not yet submission-ready. It contains a complete fold-level four-task augmentation export, but it cannot reproduce that export in place: all three experiment scripts set `ROOT` to the workspace parent and write to the sibling `JMIR_SepAware` directory. The committed augmentation CSVs are byte-for-byte copies of the sibling files. The notebook named `sepaware-vigitel-smoking-kidney-mortality.executed.ipynb` has executed display cells, but its experiment cell has `RUN=False`; it reads pre-existing CSVs and is not evidence that the experiment ran from this repository.

The paper also reports TSTR, fixed-lambda, factorial and COVID DACPF results whose raw authoritative files and executing notebooks are outside this repository. Only derived figures and hard-coded LaTeX values are present here. Those claims are traceable within the wider workspace but are not reproducible from a clean clone.

The four-task augmentation export contains 1,620 prediction rows (4 tasks x 9 conditions x 3 classifiers x 3 repeats x 5 folds) and 240 synthetic-diagnostic rows (4 tasks x 4 generator conditions x 3 repeats x 5 folds), with no duplicate experiment keys or missing metric values. This establishes row-level completeness for the augmentation benchmark only. It does not establish cross-task completeness for TSTR, fidelity or corrected statistical inference.

At audit time, 64 of 84 transferable task-experiment cells (76.2%) are complete. The incomplete transferable cells are the 8 cross-task TSTR cells, 4 fidelity cells, 8 corrected-primary-inference cells. This count treats the invalid exploratory fixed-lambda grid as superseded, not as required confirmatory evidence. The current evidence therefore does **not** support describing the repository as a complete four-task benchmark.

## A. Experiment inventory

| Experiment | Tasks | Status | Evidence in this repository | Audit decision |
|---|---|---|---|---|
| Four-task augmentation benchmark | All four | Executed externally; outputs copied here | `experiments/outputs/predictive_metrics_long.csv`, `synthetic_diagnostics_long.csv` | Numerically complete, but rerun after path/refactor fixes |
| Conventional baselines | All four | Same run as above | Fold-level prediction CSV | Complete pending provenance rerun |
| CTGAN/TVAE standard vs SepAware augmentation | All four | Same run as above | Fold-level prediction and diagnostic CSVs | Complete pending provenance rerun |
| Fixed-lambda five-fold TSTR | Vigitel obesity, COVID-19 | Executed outside repository | Derived figures and hard-coded tables only | Migrate raw files; supersede tuned grid; rerun prespecified TSTR on all tasks |
| Fixed-lambda grid selection | Vigitel obesity, COVID-19 | Executed, exploratory | No raw output here | Superseded because reporting-fold outcomes selected the setting |
| Blocked 2x2 separability-by-anchor factorial | Vigitel obesity, COVID-19 | Executed outside repository | Derived figures and hard-coded tables only | Dataset-specific mechanism analysis; migrate raw evidence and regenerate effects |
| Factorial assumption diagnostics | Vigitel obesity, COVID-19 | Executed outside repository | Hard-coded values only | Migrate and regenerate; inference remains exploratory |
| COVID DACPF | COVID-19 only | Executed outside repository | Figure and hard-coded table only | Dataset-specific; migrate raw outputs |
| Controlled prevalence-by-overlap simulation | No health task | Executed | `controlled_overlap_prevalence_*.csv` | Retain as mechanism simulation, not cross-task evidence |
| TabPFN augmentation | COVID-19 attempted | Failed dependency | No valid output | Exclude from final benchmark; document failure |
| Early single-split SepAware/ablation notebooks | Vigitel/COVID variants | Executed or partial | No authoritative outputs here | Superseded by leakage-controlled CV analyses |
| Causal-generation/filter notebooks | Dataset-specific prototypes | Protocol-only or incomplete | No authoritative outputs here | Exclude from claims |
| Cluster-then-augment | Unclear | Output not located | None | Exclude; no result is claimable |

## B. Dataset and outcome-task audit

| Task | Source | Raw shape | Executed analytic sample | Outcome | Dependence notes |
|---|---|---:|---:|---|---|
| Vigitel obesity | `vigitel2006_2023_obesidade_exclusoes.parquet` | 744,116 x 41 | 5,000; 851 positive, 4,149 negative | `desfecho`, renamed internally | Same surveillance source as smoking; source key `chave` is nonunique and requires interpretation before grouped splitting |
| COVID-19 hospital mortality | `banco_covidIH.xlsx` | 334 x 483 | All 334; 83 deaths, 251 survivors | `obito=1` | `idhosp_pcte` is unique; `record_id` is not |
| Vigitel current smoking | `Vigitel_Dataset/samples.pkl` | 21,764 x 32 | 5,000; 616 smokers, 4,384 nonsmokers | `fumante=1` | Same Vigitel source family as obesity; provided `idx` is unique |
| Kidney 365-day mortality | `tidy_event_data.feather` | 9,559,286 events, 67,267 patients | 5,000; 267 deaths, 4,733 nondeaths | first recorded death in 365 days after a 365-day landmark | Aggregated to one row per patient before splitting |

The raw data reside one directory above the repository and are not distributable from a clean clone. There is no checked-in schema, validation utility or data-placement configuration. Absolute workspace assumptions occur in notebook outputs.

## C. Status definitions and cross-task coverage

The detailed matrix is in `docs/cross_task_experiment_matrix.md`; its machine-readable counterpart is `results/experiment_coverage.csv`. `COMPLETED` means an authoritative fold-level output exists and has passed basic key/row validation. A copied output is provisionally complete numerically but still scheduled for an in-repository provenance rerun.

## D. Authoritative output map for manuscript results

| Manuscript result | Current source | Repository authority status |
|---|---|---|
| Four-task augmentation metrics | `experiments/outputs/predictive_metrics_long.csv` | Fold-level file present; executing script writes elsewhere |
| Coverage, diversity, exact match, membership proxy | `experiments/outputs/synthetic_diagnostics_long.csv` | Fold-level file present; executing script writes elsewhere |
| Naive paired generator differences | `tables/paired_sepaware_generator_differences.csv` | Derived from fold-level CSV; CI is statistically unsuitable for dependent repeated CV |
| Controlled simulation | `experiments/outputs/controlled_overlap_prevalence_long.csv` | Raw simulation output present |
| Fixed-lambda TSTR table/figure | workspace `sepaware_fixed_lambda_5fold_cv_outputs/tables/*` | Missing from repository |
| Factorial means, ANOVA, diagnostics | workspace `sepaware_factorial_cv_outputs/tables/*` | Missing from repository |
| COVID DACPF | workspace `covid_dacpf_raw_results.csv`, `covid_dacpf_summary.csv` | Missing from repository |

## E. Claims without adequate repository support

1. The abstract's Vigitel TSTR Macro-F1 change and 96% factorial allocation rely on files outside the repository.
2. All fixed-lambda, factorial and DACPF numeric tables are hard-coded rather than generated from checked-in raw outputs.
3. The manuscript calls the four-task outputs executed repository evidence, but the current scripts write to a sibling repository.
4. The paper says the SepAware normalization is robust; the augmentation implementation uses candidate-pool min-max normalization with a constant-value fallback of 0.5.
5. The paper describes lambda-controlled selection, but the augmentation script hard-codes `score = realism + separability`; no augmentation manifest records weights.
6. The current paired 95% intervals treat 45 fold-classifier differences as independent and have no corrected repeated-CV p-values or multiplicity adjustment.
7. The related comparison and narrative imply fidelity assessment across the benchmark, but the four-task run exports no marginal, dependence or classifier-based fidelity metrics.
8. TSTR is discussed as a core evaluation regime but is not executed for smoking or kidney mortality in committed outputs.

## F. Internal inconsistencies

1. `run_config.json` says one consolidated four-task run, but the files were assembled through append/resume operations and the notebook only re-reads them.
2. `partition_seed` is logged as 42, 43 and 44, although `RepeatedStratifiedKFold` is instantiated once with `random_state=42`; the stored field is descriptive, not the actual splitter seed used for each repetition.
3. The augmentation code uses 30 epochs in the committed configuration, whereas full-mode defaults to 100 epochs.
4. `make_manuscript_outputs.py` intentionally emits a LaTeX table containing only smoking and kidney mortality while surrounding text makes all-task claims.
5. Sections 3.9 and 3.10 duplicate the augmentation protocol.
6. “Minority” labels remain in output columns and tables even though “positive class” is the intended outcome definition.
7. The current title and prose were presentation-oriented; the requested journal title and neutral phrasing have not yet been applied because experiments are not finalized.

## G. Missing experiments for a fair common benchmark

- Standard and SepAware CTGAN TSTR for all four tasks.
- Standard and SepAware TVAE TSTR for all four tasks.
- Comparable four-task fidelity diagnostics.
- Corrected repeated-CV inference for both primary generator contrasts by task, including Holm adjustment, classifier and repetition sensitivity.
- Re-execution of the augmentation benchmark from code that writes within this repository and records actual configuration and source hashes.
- Automated leakage, determinism, schema and metric tests.

## H. Analyses that are not transferable

The COVID DACPF analysis requires independently motivated COVID variables (age, cancer and respiratory admission indicators). Equivalent anchors are not prespecified for the Vigitel smoking or kidney tasks. Inventing anchors after observing results would create outcome-guided tuning. The separability-by-anchor factorial therefore remains limited to tasks with independently defined anchors. The controlled prevalence-by-overlap simulation is not a health-task experiment and must not enter cross-task averages. Temporal validation is not available for the smoking sample because it lacks a survey-year field; this does not excuse missing non-temporal benchmark experiments.

## I. Leakage, tuning and statistical-validity risks

1. The augmentation script splits before median imputation and fits imputation/scaling on each training fold, which is appropriate.
2. Generator fitting and candidate scoring use training data only; standard and selected variants share a pool.
3. Held-out prevalence is retained and the 0.5 threshold is fixed.
4. Kidney data are aggregated to one patient row before splitting, which prevents patient overlap.
5. Vigitel obesity uses row-level splitting while `chave` is nonunique in the raw extract. The meaning of this field must be established; if it identifies repeat respondents, grouped splitting is required.
6. The fixed-lambda grid selected settings on reporting folds and must remain exploratory/superseded.
7. Repeated folds overlap, classifier results share folds, and generator variants share pools. Naive t intervals over 45 observations understate dependence.
8. The membership proxy is a nearest-synthetic heuristic, not a calibrated membership-inference attack or privacy guarantee.
9. TVAE is fitted only to positive-class features because native conditional sampling is unavailable. Standard-vs-selected TVAE remains paired, but CTGAN-vs-TVAE comparisons are not symmetric.
10. No raw predictions are exported, limiting independent recalculation of threshold-free metrics and pooled calibration curves.

## J. Proposed final experiment matrix and execution order

1. Refactor the authoritative code into `code/src/sepaware` with repository-relative outputs and configured external data roots.
2. Add the manifest, schema validators, input hashes, environment lock and tests before rerunning models.
3. Implement one fold runner that exports split indices, raw predictions, candidates/diagnostics, timing and metadata for augmentation and TSTR.
4. Run a smoke configuration on non-sensitive simulated data and execute the test suite.
5. Rerun the nine-method augmentation benchmark for all four tasks using the frozen 3 x 5 protocol and recorded seeds.
6. Run standard/SepAware CTGAN and TVAE TSTR on the same task splits.
7. Generate common fidelity, positive-class coverage/diversity, exact-match and membership-proxy outputs.
8. Generate corrected repeated-CV contrasts and Holm-adjusted results from raw fold/repetition summaries.
9. Migrate and validate the original factorial and DACPF raw evidence; rerun only if the code/output mismatch cannot be reconciled.
10. Build all tables and figures from exported data, then revise the manuscript.

## Execution gate

The manuscript will not be rewritten until the common benchmark, TSTR, fidelity and primary statistical outputs are finalized. Dataset-specific DACPF and anchor-factorial results will be presented after the common benchmark and will not be used to fill missing cross-task cells.

## Post-audit execution addendum

The gate was satisfied after the audit. The four-task augmentation benchmark was rerun into `results/raw/predictive_metrics_long.csv` (1,620 rows) and `synthetic_diagnostics_long.csv` (240 rows). The cross-task TSTR/fidelity run produced `tstr_fold_metrics.csv` (720 rows) and `tstr_diagnostics.csv` (240 rows), with no missing values or duplicate experiment keys. Corrected primary inference was regenerated in `results/statistical_tests/`. The final coverage matrix records 84/84 transferable cells completed. This addendum does not alter the pre-change findings above; it records how their execution gate was closed.
