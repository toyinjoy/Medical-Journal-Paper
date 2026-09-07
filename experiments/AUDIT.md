# Evidence and reproducibility audit

## Existing manuscript

The draft in `Computer-Medicine-Paper/journal_manuscript` is a substantial manuscript, but it targets Computers in Biology and Medicine through `elsarticle`, not JMIR. It already contains an introduction, related work, methods, results, discussion, limitations, conclusion, declarations, and supplementary section. It will be used as a content source, not as the final journal package.

## Executed evidence suitable for the initial paper

- Two datasets: a 5,000-record Vigitel obesity sample and a 334-record COVID-19 mortality cohort.
- Leakage-aware five-fold CTGAN/SepAware experiments with explicit TSTR labeling.
- Fixed-lambda results for standard CTGAN and SepAware.
- A replicated blocked 2x2 separability-by-anchor factorial analysis.
- Exported fold-level classifier results, fidelity summaries, separability summaries, correlations, ANOVA allocations, and assumption diagnostics.
- A separate COVID-19 real-plus-synthetic domain-anchor filtering experiment.

## Key established findings

- Vigitel: SepAware TSTR Macro-F1 is about 0.583 versus about 0.459 for standard CTGAN; the factorial analysis attributes approximately 96% of treatment-plus-error variation to separability pressure.
- COVID-19: the fixed balanced setting reaches about 0.549 Macro-F1 versus about 0.463 for standard CTGAN, but uncertainty is wide; the factorial separability contribution is about 5%, with residual error above 81%.
- The contrast supports a dataset-dependent effect and does not support universal superiority.

## Issues requiring correction or explicit treatment

1. The current journal draft is not in a JMIR-compatible structure.
2. Its abstract relies heavily on Macro-F1 and describes requested analyses as future work.
3. Several source notebooks impute some features before cross-validation during dataset loading. New experiments must move every learned preprocessing operation inside the training fold.
4. The existing five-fold factorial scores are paired but are not independent replications because training folds overlap and conditions share candidate pools.
5. The qualification grid selected lambda settings on the reporting folds; it must remain exploratory. New runs use a fixed setting.
6. Vigitel's anchor list currently contains every predictor, making the anchor term closer to global conditional compatibility than a small domain-anchor set. This must be described accurately or narrowed prospectively.
7. Existing duplicate checks are not a sufficient privacy evaluation.
8. The current experiments do not establish minority phenotype preservation or boundary-case retention.
9. The current draft uses placeholder authorship and correspondence details, which cannot be inferred.

## Source-paper relevance

- `BHI_HealthSyn-Copy-/main.pdf` is directly relevant to Vigitel, health-survey synthesis, utility, coverage, and privacy. It may inform context and evaluation while avoiding textual reuse.
- `_CIKM_2026__SyntheticGIST___Anne.pdf` and `25292_Camera_Ready_PDF_File (1).pdf` concern causal structure learning. They are principally relevant to the planned causal-generation paper, not the central claims of this paper.

## Environment finding

The pre-existing Anaconda environment paired NumPy 2.2.6 with extensions compiled against NumPy 1.x, causing pandas, scikit-learn, SDV, CatBoost, and plotting imports to fail. A project-local `.venv-jmir` environment was created with NumPy 1.26.4 layered over the existing packages. No global package was changed.

