# Final cross-task experiment coverage

The pre-change status was audited at commit `b8b4276`; the table below reflects the completed repository-local reruns. Evidence paths and applicability decisions are in `results/experiment_coverage.csv`.

| Experiment | Vigitel obesity | COVID mortality | Vigitel smoking | Kidney mortality |
|---|---|---|---|---|
| Real-only augmentation baseline | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Random oversampling | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Random undersampling | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| SMOTE | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Class-weighted learning | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Standard CTGAN augmentation | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| SepAware CTGAN augmentation | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Standard TVAE augmentation | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| SepAware TVAE augmentation | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Standard CTGAN TSTR | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| SepAware CTGAN TSTR | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Standard TVAE TSTR | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| SepAware TVAE TSTR | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Discrimination and calibration metrics | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Positive-class coverage and diversity | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Exact-match diagnostics | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Membership-inference proxy | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Common fidelity diagnostics | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Corrected CTGAN primary contrast | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Corrected TVAE primary contrast | COMPLETED | COMPLETED | COMPLETED | COMPLETED |
| Dataset-specific clinical anchors/DACPF | NOT_TRANSFERABLE | COMPLETED | NOT_TRANSFERABLE | NOT_TRANSFERABLE |
| Separability-by-anchor factorial | COMPLETED | COMPLETED | NOT_TRANSFERABLE | NOT_TRANSFERABLE |
| Controlled prevalence-overlap simulation | NOT_TRANSFERABLE | NOT_TRANSFERABLE | NOT_TRANSFERABLE | NOT_TRANSFERABLE |
| Reporting-fold fixed-lambda grid | SUPERSEDED | SUPERSEDED | SUPERSEDED | SUPERSEDED |

Transferable completion: **84/84 cells (100%)**. All scientifically transferable cells in the prespecified matrix have authoritative outputs. This supports describing the work as a complete four-task common benchmark, while not treating the two Vigitel tasks as independent source replications. Dataset-specific clinical anchors remain outside the common benchmark for the reasons recorded above.
