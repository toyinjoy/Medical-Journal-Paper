# JMIR SepAware manuscript package

This directory is the Overleaf-ready authoring package for the four-task paper:

> Improving Rare-Outcome Prediction With Separability-Aware Synthetic Health Data: A Four-Task Validation Study

## Compile

Upload the directory to Overleaf as a ZIP and set `main.tex` as the main document. The project uses standard TeX Live packages and BibTeX.

If the Overleaf PDF still shows the old two-dataset title or `[Alex: ...]` annotations, Overleaf is compiling an older project or a different main document. Confirm that the project is synchronized to the latest `main` branch and that `main.tex` is selected under **Menu > Main document**. The smoking and kidney-mortality findings appear in Section 4.4, **Strengthened augmentation comparison across four tasks**, and Table 9. A ready-to-read compiled copy is stored at `output/pdf/Improving_Rare_Outcome_Prediction_With_Separability_Aware_Synthetic_Health_Data.pdf`.

Local compilation used:

```sh
tectonic main.tex
```

## Project structure

- `main.tex`: manuscript entry point and structured abstract.
- `sections/`: manuscript sections and supplementary audit.
- `references.bib`: verified foundational and recent references.
- `figures/`: existing qualification figures plus strengthened experiment figures.
- `tables/`: manuscript-ready tables and tidy CSV summaries.
- `experiments/PROTOCOL.md`: prospective strengthened-study decisions.
- `experiments/AUDIT.md`: evidence, environment, and protocol audit.
- `experiments/run_strengthened_experiments.py`: four-task augmentation analysis.
- `experiments/run_controlled_overlap_prevalence.py`: independent prevalence-by-overlap mechanism experiment.
- `experiments/make_manuscript_outputs.py`: deterministic tables and figures.
- `experiments/outputs/`: fold-level and summarized outputs.

The executed experiment notebook is stored in `experiments/sepaware-vigitel-smoking-kidney-mortality.executed.ipynb`.

## Items the authors must complete

Information that requires author confirmation is tracked in `MANUSCRIPT_UNRESOLVED_COMMENTS.md` rather than displayed in the presentation PDF:

- Full author list, degrees, affiliations, ORCIDs, and corresponding-author details.
- Ethics committee or IRB name, approval/exemption number, consent or waiver, and compensation statement.
- Funding and article-processing-charge support.
- Conflicts of interest.
- CRediT author contributions.
- Exact Vigitel access route and extract version.
- COVID-19 source institution and permitted data-availability wording.
- Public code repository DOI/URL and license.

Do not remove these placeholders by guessing.

## Interpretation boundaries

- The original factorial analysis is TSTR; the strengthened analysis is real-plus-synthetic augmentation. They are not pooled.
- The new run uses three independently shuffled 5-fold partitions, fold-specific generator seeds, and 30 generator epochs.
- Random oversampling is highly competitive and must remain prominent.
- SepAware improves CTGAN modestly but does not improve TVAE in this run.
- Improved CTGAN coverage accompanies lower minority diversity.
- Exact-match and membership-proxy results are not a privacy guarantee.
- Four outcome tasks from three health-data sources broaden validation but do not establish general clinical validity.
