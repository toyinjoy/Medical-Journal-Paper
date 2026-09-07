# Literature and journal-format audit

Checked on 2026-08-23.

## High-priority recent publications integrated

- Huet-Dastarac M, Dankar FK, Liu D, et al. An Evaluation of Pretrained Generative Models for Augmenting Small Health Data: Comparative Modeling Study. *Journal of Medical Internet Research*. 2026;28:e88678. doi:10.2196/88678. PMID:42296511. This paper directly motivates the sampling-with-replacement comparator and cautions that increased sample count can explain apparent augmentation gains.
- Nanevski I, Mohebi M, Jäger S, et al. Evaluating the Quality of Tabular Synthetic Data in Health Care. *PLOS Digital Health*. 2026;5(7):e0001522. doi:10.1371/journal.pdig.0001522. PMID:42412881. This supports joint evaluation of fidelity, utility, and privacy and the conclusion that no generator dominates every dataset and metric.
- Hernandez M, Osorio-Marulanda PA, Catalina M, et al. Comprehensive Evaluation Framework for Synthetic Tabular Data in Health. *Frontiers in Digital Health*. 2025;7:1576290. doi:10.3389/fdgth.2025.1576290. This supports multidimensional evaluation and explicit TSTR/TRTR separation.
- Kaabachi B, Despraz J, Meurers T, et al. A Scoping Review of Privacy and Utility Metrics in Medical Synthetic Data. *npj Digital Medicine*. 2025;8:60. doi:10.1038/s41746-024-01359-3. This supports the privacy-risk caveats and stronger attack requirements.
- Isasa I, Catalina M, Epelde G, et al. Synthetic Tabular Data Generation Under Horizontal Federated Learning Environments in Acute Myeloid Leukemia: Case-Based Simulation Study. *JMIR Medical Informatics*. 2025;13:e74116. doi:10.2196/74116. This was reviewed as a recent JMIR-family example of synthetic tabular health-data reporting.

## JMIR requirements reflected in the package

- Structured abstract with Background, Objective, Methods, Results, and Conclusions.
- Main sections aligned as Introduction, Methods, Results, and Discussion.
- Ethical Considerations subsection and explicit completion flag.
- Required Funding, Conflicts of Interest, and Abbreviations sections.
- Numerical citation style.
- Tables placed near first discussion and kept compact; extended material routed to the supplement.
- Figure outputs are high-resolution PNG.
- AI-use disclosure included for author review.
- Main text kept below the journal's 10,000-word fee threshold target.

The JMIR submission system ultimately expects author metadata and may prefer a Word manuscript for production. This LaTeX package is intended for Overleaf collaboration and PDF review; authors should verify the destination journal's file-upload requirements at submission time.
