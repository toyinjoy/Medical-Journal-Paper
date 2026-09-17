# JMIR advisor comments: response and implementation tracker

Source reviewed: email from Marcos Goncalves, August 11, 2026, supplied as
`Gmail - Recipe for the JMIR paper nbased on the Thesis Proposal.pdf`.

This tracker separates changes that can be made defensibly now from analyses that
must remain pending until new experiments have been run. No result should be
described as completed merely because the manuscript now proposes it.

## 1. Reframe the paper around a scientific question

**Comment.** Do not present the work simply as a new synthetic-data method. Ask
when synthetic data help rare-outcome prediction and what separability adds beyond
class imbalance.

**Response: addressed in the manuscript.** The title, abstract, research questions,
contribution statement, discussion, and conclusion now lead with the conditional,
mechanism-oriented claim. Universal-superiority language is explicitly rejected.

## 2. Treat Vigitel/COVID heterogeneity as a result

**Comment.** The strong Vigitel effect and weak/uncertain COVID effect should be
explained rather than hidden.

**Response: addressed in the manuscript.** Cross-dataset heterogeneity is central
to the abstract, Results, Discussion, Limitations, and Conclusion. The COVID null is
not characterized as a failed experiment.

## 3. Add health datasets with different imbalance and overlap

**Comment.** Two datasets are insufficient; use approximately 4--6 health datasets.

**Response: addressed for the agreed scope.** Vigitel current smoking and
landmark-defined 365-day kidney mortality were executed as tasks 3 and 4. Dialysis
was excluded by author decision because a defensible incident endpoint requires
additional code validation and competing-risk handling. The manuscript reports four
tasks from three sources and does not treat the two Vigitel outcomes as independent
sources. See `DATASET_OUTCOME_VALIDATION.md` for the audit and cohort rules.

## 4. Add strong baselines

**Comment.** Compare real-only training, random over/undersampling, SMOTE, class
weighting, standard CTGAN, SepAware, and at least one modern generator.

**Response: substantially addressed.** The strengthened benchmark uses identical outer
splits and preprocessing for all methods. Minimum baseline set: real-only,
class-weighted real-only, random oversampling, random undersampling, SMOTE, standard
CTGAN, TVAE, and SepAware applied to both CTGAN and TVAE. TabDDPM is desirable but
should not block the minimum study if compute or implementation validation is
insufficient. Gaussian copula may be retained as a transparent non-neural generator.

**Decision rule.** Do not tune each method on the outer test folds. Hyperparameters,
including SepAware weights, are selected in an inner validation loop or fixed in a
written protocol before outer-fold evaluation.

## 5. Show that selection is generator-agnostic

**Comment.** Apply SepAware to more than CTGAN.

**Response: addressed.** SepAware was applied to CTGAN and TVAE. The result is an
important negative boundary condition: selection was beneficial for CTGAN on three
tasks but not kidney mortality and was not consistently beneficial for TVAE. The
matched standard and selected conditions share each fitted generator and candidate
pool. A formal method-by-generator hierarchical interaction remains pending.

## 6. Strengthen replication and statistical inference

**Comment.** Use repeated partitions, independent generator seeds, and predefined
SepAware settings.

**Response: partially addressed.** The study now uses three repeated five-fold
partitions and fold-specific generator fits. The kidney cohort is patient-level, so
no patient crosses folds. Generator fits vary by fold and the SepAware setting was
fixed before evaluation. External temporal validation, multiple generator seeds per
fold, and a full hierarchical model retaining source remain pending. Overlapping CV
folds are not interpreted as independent samples.

## 7. Expand predictive and calibration metrics

**Comment.** Go beyond Macro-F1.

**Response: addressed for the strengthened experiment.** AUPRC is the primary rare-outcome
ranking metric. Macro-F1, positive-class F1, precision, recall, balanced accuracy,
AUROC, Brier score, and calibration intercept/slope are exported. Thresholds are not
optimized on the outer test fold. Calibration plots and decision-curve analysis
remain pending because clinically justified decision thresholds are not available.

## 8. Test minority diversity, coverage, and boundary behavior

**Comment.** Determine whether SepAware recovers signal or merely removes difficult
but valid cases.

**Response: partially addressed and elevated to a central safety analysis.** The
executed runs measure nearest-synthetic minority coverage and within-minority
diversity. They show better coverage but lower diversity. Boundary-stratified errors,
subgroup retention, and externally defined phenotype coverage remain pending. A
utility gain accompanied by material loss of clinically meaningful coverage is not
counted as success.

## 9. Add privacy-risk evaluation

**Comment.** Exact-duplicate checks are insufficient.

**Response: partially addressed.** Exact matches and a nearest-synthetic
membership-inference proxy are reported. Attribute inference, rarity-stratified
attacks, canary tests, and a stronger explicit attacker model remain pending. The
manuscript does not claim that synthetic data are anonymous or inherently safe.

## 10. Analyze overlap versus SepAware benefit

**Comment.** Make the relationship between intrinsic class overlap and improvement
over standard generation a main figure.

**Response: accepted; pending.** For each outer training split, estimate overlap
using multiple complementary measures (for example, neighborhood disagreement,
cross-validated probabilistic classification error, and a geometry-based index).
Compute SepAware minus matched-generator utility on the untouched outer test fold.
Plot task-level estimates with uncertainty. Avoid a simple correlation over five
task averages; use fold/seed-level hierarchical modeling and sensitivity analysis
across overlap estimators.

## 11. Manipulate prevalence and overlap independently

**Comment.** Run a controlled prevalence-by-overlap experiment.

**Response: addressed as a controlled mechanism experiment.** The completed
simulation varies prevalence and overlap independently and compares real-only,
random oversampling, SMOTE, and SepAware-SMOTE across two classifiers and fixed
factor levels. It does not establish a significant SepAware interaction, which is
reported rather than hidden.

## 12. Determine how much separability is too much

**Comment.** Study the utility--coverage trade-off across separability strength.

**Response: accepted; pending.** Report a prespecified SepAware strength curve with
utility, calibration, minority coverage, and privacy risk on aligned axes. Select no
single best weight from the outer test results. Identify a Pareto region and define a
failure threshold for coverage loss before analysis.

## 13. Keep causal generation for a separate paper

**Comment.** Studies 3 and 4 would weaken the JMIR story if included in full.

**Response: addressed editorially.** The JMIR manuscript is scoped to imbalance,
overlap, separability, utility, diversity, and privacy. Existing domain-anchor results
may appear only as secondary motivation/ablation. Claims of causal generation,
structure discovery, graph-informed diffusion, and causal effect identification are
reserved for a separate paper.

## 14. External or temporal validation

**Comment.** Include at least one external/temporal validation if possible.

**Response: accepted; feasibility pending.** A calendar-time split is natural for the
kidney event log if data coverage and care pathways are sufficiently stable. Vigitel
survey years can also support temporal validation if year is available in the source
data; the supplied `samples.pkl` does not contain an explicit survey-year field.
Temporal splitting must occur before all preprocessing and generation. A second
outcome from the same kidney source is not external validation.

## Comments that need qualification rather than literal implementation

- **"4--6 health datasets":** five outcome tasks are available, but only three
  sources. The manuscript must say "five dataset-outcome tasks from three sources,"
  not "five independent datasets."
- **Dialysis as a rare outcome:** in the raw kidney log, 44,591/67,267 patients
  (66.29%) ever have a dialysis event and 15,831 first appear on a dialysis date.
  Ever-dialysis is therefore neither rare nor a valid prospective endpoint. Only
  incident dialysis after a clean baseline is suitable.
- **AUPRC as an endpoint:** essential, but it varies with prevalence. Compare methods
  within the same task/test set and report prevalence; do not rank raw AUPRC across
  outcomes with different base rates.
- **"Separability explains 96%":** this is conditional on the current factorial
  decomposition and overlapping folds. It must not be generalized to population
  variance or new datasets without independent seeds and hierarchical inference.
- **Causal anchors:** clinically motivated associations are not causal evidence.
  Preserve the narrow "domain-anchor" terminology in this paper.

## Completion criterion

A comment is marked completed only when its prespecified output exists, passes
leakage and reproducibility checks, and is incorporated into the manuscript with an
effect estimate and uncertainty. Until then, it remains an accepted action item.
