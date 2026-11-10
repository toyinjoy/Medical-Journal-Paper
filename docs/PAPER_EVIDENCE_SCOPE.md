# CTGAN-only paper evidence scope

Date: 2026-11-09

## Scientific question

The paper tests whether post-generation curation changes synthetic-to-real minority classification when CTGAN, the candidate pool, class quotas, downstream classifiers, and threshold policy are matched. It does not compare generator families.

## Confirmatory evidence

- `results/ctgan_locked/locked_summary.csv`: locked metric means for Standard CTGAN and threshold-aware SepAware.
- `results/ctgan_locked/locked_inference.csv`: primary minority-F1 effects, feature-group bootstrap intervals, paired-model wins, prediction-swap permutation tests, and Holm adjustment.

The locked candidate used 30 CTGAN epochs, three generator seeds, a five-times candidate pool, logistic regression, random forest, CatBoost, and thresholds learned only from grouped synthetic-training predictions.

## Mechanism evidence

- `results/ctgan_locked/mechanism_summary.csv`: saved-pool coverage, selected-set overlap, and progressive replacement effects.
- Distribution and epoch-budget values in the manuscript come from the validated October 2026 audit packages in the parent research workspace. They are sensitivity/mechanism evidence and are not pooled with the internal lock.

## Historical outputs

Historical repository files include development comparisons with other generators. They are retained to preserve the audit trail but are excluded from the paper's title, abstract, methods, tables, inference, discussion, conclusion, and reproduction claims. Removing them from the filesystem would erase completed research evidence without improving the validity of the CTGAN-only question.

## Previous CTGAN study

The manuscript states that CTGAN was fixed based on the preceding development study. A formal self-citation should be added only if that study has a citable public or accepted version; see `MANUSCRIPT_UNRESOLVED_COMMENTS.md`.
