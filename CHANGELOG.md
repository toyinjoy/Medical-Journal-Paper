# Scientific and editorial changelog

## 2026-09-17: submission-readiness rebuild in progress

### Audited

- Inventoried manuscript, code, notebooks, outputs, raw data locations, software versions and Git state.
- Distinguished four outcome tasks from three data sources.
- Verified the committed augmentation export has the expected 1,620 prediction and 240 diagnostic rows.
- Identified sibling-directory output routing, nonexecuting “executed” notebook cells, missing TSTR/fidelity coverage and naive dependent-fold intervals.
- Recorded pre-change coverage as 64/84 transferable cells (76.2%).

### Changed

- Added a machine-readable experiment manifest with source hashes and task definitions.
- Added repository-local importable modules for data construction, robust SepAware scoring, evaluation, diagnostics and corrected statistics.
- Defined robust component normalization as median/MAD z-scaling, IQR fallback, clipping to +/-3 and mapping to [0,1].
- Defined deterministic quota selection and candidate-shortfall failure.
- Changed experiment output routing from the sibling `JMIR_SepAware` directory to `results/raw`.
- Changed repeated-CV split construction to explicit partition seeds 42, 43 and 44.
- Added schema/hash validation and automated leakage, selection, metric and reproducibility tests.

### Executed

- Source validation for all four tasks: passed with expected class counts.
- Unit test suite: 5 passed.
- Augmentation and TSTR smoke runs: passed; smoke outputs excluded from authoritative results.
- Full four-task augmentation benchmark rerun in this repository: 1,620 fold--classifier results and 240 generator-diagnostic rows, with no missing or duplicate experiment keys.
- Corrected primary statistics regenerated from the authoritative rerun. Only Vigitel smoking SepAware CTGAN versus standard CTGAN excluded zero after Holm adjustment; seven other primary intervals included zero.
- Completed cross-task TSTR, fidelity, coverage, diversity, exact-match, and membership-proxy run: 720 metric rows and 240 diagnostic rows, with no missing or duplicate keys.
- Recorded the kidney TVAE exact-match finding (10.5% standard; 13.4% selected) as a release risk rather than suppressing it.
- Migrated executed factorial and COVID DACPF raw outputs and their executed notebooks into the repository.

### Excluded or unresolved

- Reporting-fold lambda tuning remains exploratory and is superseded for confirmatory claims.
- COVID DACPF and the anchor factorial remain dataset-specific.
- Ethics, funding, author contributions and data-access language require author confirmation.
- The nonunique Vigitel obesity `chave` field requires data-owner interpretation before claiming participant-level independence.

### Manuscript revision

- Changed the title to “Separability-Aware Synthetic Data Selection for Rare-Outcome Prediction in Health Data.”
- Replaced the incomplete selection description with equations matching the implementation and Algorithm 1.
- Merged duplicated augmentation-method subsections and separated common benchmark results from dataset-specific anchor analyses.
- Replaced legacy point estimates with values generated from the authoritative rerun and removed independent-fold language.
- Added the complete four-task augmentation table, corrected primary-contrast figure, and TSTR table generator.
- Corrected LaTeX diacritics for Jäger, Fürstenau, Müller, and Körfer.
