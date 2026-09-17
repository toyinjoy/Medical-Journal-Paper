# SepAware two-dataset JMIR protocol

Version: 0.1 (prospective extension of the completed qualification experiments)

## Objective

Estimate when class-separability-aware selection improves rare-outcome prediction beyond class-frequency correction, and test whether any improvement is accompanied by loss of minority coverage or increased disclosure risk.

## Scope

- Dataset-outcome tasks: Vigitel obesity, COVID-19 hospital mortality, Vigitel current smoking, and 365-day kidney-cohort mortality.
- Current status: a four-task validation study from three underlying data sources. Results are not presented as universal or externally validated, and the two Vigitel tasks are not treated as independent sources.
- Confirmatory endpoint: held-out-real-data AUPRC under the real-plus-synthetic augmentation regime.
- Key secondary endpoints: Macro-F1, minority F1, sensitivity, precision, AUROC, balanced accuracy, Brier score, and calibration slope/intercept.
- Existing synthetic-to-real factorial results remain a separate component-attribution analysis and are not pooled with augmentation results.

## Data splits and repetitions

- Repeated stratified cross-validation with all preprocessing fitted within each real training fold.
- Five folds and three independent partition seeds for the initial manuscript run.
- Generator seed is varied independently within each partition/fold.
- All methods within a partition/fold share the same held-out real observations.
- Vigitel uses the qualification's reproducible 5,000-record stratified sample; COVID-19 uses all eligible records.
- Vigitel smoking uses a reproducible 5,000-record stratified sample from `samples.pkl`; identifiers, cluster labels, and `color` are excluded.
- Kidney mortality uses a 365-day landmark after first recorded activity, a subsequent 365-day death horizon, and only patients with a recorded death in-horizon or observable activity through the horizon. Features are counts computed strictly before the landmark. Patients who died before the landmark are excluded. A reproducible stratified sample of 5,000 eligible patients is used for computational comparability.
- Dialysis is not an outcome in this study. Pre-landmark dialysis counts may be used as mortality predictors because they would be observable at prediction time.

## Methods

1. Real-only training.
2. Random oversampling.
3. Random undersampling.
4. SMOTE.
5. Class-weighted training.
6. Standard CTGAN augmentation.
7. SepAware-selected CTGAN augmentation.
8. TVAE augmentation.
9. SepAware-selected TVAE augmentation.

Synthetic augmentation generates minority-class candidates using only the real training fold. Standard-generator and SepAware conditions use the same candidate pool whenever possible. The SepAware setting is fixed prospectively at lambda_sep=1.0 and lambda_anchor=0.5; no test-fold result is used to tune it.

## Predictive models

- Regularized logistic regression (linear, calibrated reference).
- Random forest (nonlinear reference).
- CatBoost (strong tabular learner).

Hyperparameters are fixed before outcome comparison. Model-specific class weighting is used only in the named class-weight condition.

## Overlap and prevalence experiment

Prevalence and overlap are manipulated independently in a controlled simulation. This benchmark is a mechanism experiment, not an additional clinical dataset.

- 2,000 observations, 15 features, 8 informative features, 3 redundant features, and 2 clusters per class.
- Prevalence levels: 5%, 15%, and 30%.
- Separation levels: 0.4 (high overlap), 1.0 (moderate overlap), and 2.0 (low overlap).
- Label noise: 2%.
- Ten independent data seeds with stratified 70/30 train-test splits.
- Methods: real only, random oversampling, SMOTE, and SepAware-selected SMOTE candidates.
- Classifiers: logistic regression and random forest.
- Analysis tests method-by-overlap and method-by-prevalence interactions with heteroscedasticity-robust standard errors.

Simulation results are interpreted mechanistically and are not combined with natural-data performance estimates.

## Diversity, boundary, fidelity, and privacy checks

- Minority nearest-neighbour coverage of held-out real minority cases.
- Within-minority pairwise-distance distribution and effective cluster coverage.
- Distance of selected candidates to a training-fold decision boundary.
- Class-conditional marginal and correlation fidelity.
- Exact matches and distance to closest real training record.
- Membership-inference proxy based on train-versus-holdout nearest-neighbour distances, with AUROC and uncertainty.

## Statistical analysis

- Report fold/seed-level estimates and paired method differences with 95% confidence intervals.
- Use hierarchical/mixed-effects regression with partition/fold grouping for the strengthened experiment.
- Treat dataset and classifier as prespecified factors; emphasize effect sizes and uncertainty.
- For the controlled experiment, estimate method-by-overlap and method-by-prevalence interactions.
- Do not treat overlapping cross-validation folds as independent laboratory replications.
- Apply false-discovery-rate correction to families of secondary pairwise comparisons.

## Decision rules

SepAware is considered supported for a dataset only if it improves held-out-real AUPRC relative to the corresponding standard generator and does not show a material deterioration in minority coverage, calibration, or privacy proxy. Macro-F1 improvement alone is insufficient.

## Reporting constraints

- Separate TSTR, real-plus-synthetic augmentation, and real-only evaluation throughout.
- Label the varied-lambda qualification grid exploratory.
- Label the two-dataset extension initial validation.
- Do not claim privacy preservation from duplicate checks alone.
- Do not claim clinical phenotype preservation without an externally justified phenotype definition.
