# Dataset and outcome suitability audit

Audit date: September 7, 2026.

## Executive decision

The files support the two additional prediction tasks selected for this paper:

- `tidy_event_data.feather`: used for landmark-defined **365-day recorded death**.
  Incident dialysis remains technically possible but was excluded from this paper.
- `Vigitel_Dataset/samples.pkl`: suitable for a cross-sectional **current-smoking**
  outcome (`fumante`), subject to provenance, survey-design, and feature-definition
  checks.

The executed paper therefore contains four outcome tasks from three underlying
sources. The two Vigitel tasks are not treated as independent sources.

## Observed file characteristics

### Kidney event log

- 9,559,286 rows, 67,267 patients, 6,207 event codes.
- Date range represented by 5,822 unique dates.
- 25,072 patients (37.27%) have a `DEATH` event.
- 44,591 patients (66.29%) have at least one `EVENT_C1DIALISE_HD` or
  `EVENT_C1DIALISE_DP` event.
- 18,817 have both death and dialysis recorded.
- Among patients with both, death is after first dialysis for 18,362, on the same day
  for 12, and before first recorded dialysis for 443.
- 15,831 patients first appear on their first dialysis date.

These counts demonstrate why naive row-level or ever/never modeling would be
invalid: dialysis is common, many patients enter the data already receiving it, and
post-outcome events could trivially leak the label.

### Vigitel smoking sample

- 21,764 records and 32 fields.
- `fumante=1`: 2,683 (12.33%); `fumante=0`: 19,081 (87.67%).
- No missing values or exact duplicate rows were observed in the supplied file.
- The object is a list of dictionaries, not a pandas table on disk.
- `idx` is unique and must be excluded from modeling.
- `color` and the two `cluster_hier_*` fields may encode upstream clustering or
  geography and require provenance checks before inclusion.

## Executed kidney mortality cohort design

Create one patient-level prediction row per eligible index date. Do not randomly
split event rows.

### Common design elements

1. Define the clinical population and a reproducible index event (for example, first
   qualifying CKD encounter) using a code list reviewed by a domain expert.
2. Require a baseline observation window, provisionally 180 or 365 days, before the
   index date. Perform sensitivity analysis over the chosen window.
3. Construct features exclusively from events before the index date (or before the
   prediction cutoff for landmark designs).
4. Define a fixed prediction horizon, provisionally 180 and/or 365 days, and require
   sufficient follow-up or an explicit censoring model.
5. Split by patient. Prefer temporal outer validation; if multiple institutions are
   encoded and sufficiently populated, consider site-based external validation.
6. Treat competing risks explicitly where relevant. Death before dialysis prevents
   subsequent dialysis and cannot simply be labeled as an ordinary negative.
7. Validate event-code semantics and distinguish hemodialysis from peritoneal
   dialysis only if clinically justified; the primary dialysis endpoint can combine
   both modalities.

### Task A: all-cause death

- Label: death within the prespecified horizon after index.
- Exclude `DEATH` and all events timestamped at or after the prediction cutoff from
  predictors.
- Clarify whether absence of `DEATH` means survival or missing/out-of-system death.
- For incomplete follow-up, use survival analysis or exclude/censor according to a
  prespecified rule; do not label all unobserved deaths as zero automatically.
- Dialysis history before index may be a predictor if the intended deployment has it
  available, but the prediction population must then be stated clearly.

### Task B: incident kidney replacement therapy/dialysis

- Eligibility: no hemodialysis or peritoneal-dialysis event before or at index and a
  clinically justified dialysis-free washout/baseline period.
- Label: first qualifying dialysis event within the prediction horizon.
- Death before dialysis is a competing event. Preferred analysis: cause-specific or
  subdistribution time-to-event modeling; for a binary benchmark, report a clear
  competing-risk rule and sensitivity analysis.
- Patients whose first recorded event is dialysis are prevalent users and must not
  enter the incident-dialysis prediction cohort as positives.
- Confirm that acute dialysis, chronic maintenance dialysis, procedure coding, and
  administrative duplicates can be distinguished. If not, label the endpoint more
  cautiously as "first recorded dialysis" rather than chronic kidney failure.

### Why not default to multitask learning

Death and dialysis are related and could eventually be modeled jointly, but a
multitask model would change the scientific question and complicate competing-risk
interpretation. For the JMIR validation, use two parallel tasks and identical method
comparisons. A later secondary analysis may compare single-task and multitask models
if clinically motivated and powered.

## Recommended Vigitel smoking design

- Target: `fumante` (current smoker), positive prevalence 12.33%.
- Exclude `idx` unconditionally.
- Exclude `color` and `cluster_hier_str_setor_label` unless their construction is
  documented and shown not to use `fumante` or a downstream representation learned
  from the full dataset. `cluster_hier_str_setor_num` requires the same check.
- Identify fields that are direct components or near-synonyms of the smoking
  definition. Exclude them to prevent target leakage.
- Confirm survey year, city/region, sampling weights, and the exact source wave(s).
  The supplied file contains no explicit year field, so it cannot by itself support a
  transparent temporal validation or survey-weighted population claim.
- Because obesity and smoking tasks may use overlapping Vigitel respondents, keep
  their records in the same folds if compared jointly and cluster pooled uncertainty
  by Vigitel source/sample.
- Report survey-weighted results if the intended claim concerns the Brazilian adult
  population; otherwise describe the analysis as predictive performance in the
  supplied analytic sample.

## Leakage checklist before any generator is trained

- Outcome definition and code list frozen.
- Index date, baseline window, horizon, and censoring rule frozen.
- Patient/source grouping applied before preprocessing.
- No post-index events in predictors.
- IDs, outcome-derived clusters, administrative dispositions, and direct outcome
  proxies removed.
- Imputation, encoding, scaling, feature selection, overlap estimation, generator
  fitting, candidate selection, threshold tuning, and calibration confined to the
  training/inner-validation data.
- Synthetic records never enter the real outer test set.
- Method comparisons reuse identical outer test patients.

## Go/no-go criteria

Proceed with the kidney tasks only after event-code definitions, index-date logic,
follow-up completeness, and competing-risk handling are confirmed. Proceed with the
Vigitel smoking task only after variable provenance and survey metadata are obtained.
Until those checks are complete, all three are candidate validation tasks, not
submission-ready evidence.
