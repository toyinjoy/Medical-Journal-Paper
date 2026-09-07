#!/usr/bin/env python3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "JMIR_SepAware" / "experiments" / "outputs"
TABLE = ROOT / "JMIR_SepAware" / "tables"
FIG = ROOT / "JMIR_SepAware" / "figures"
TABLE.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid", context="paper")

p = pd.read_csv(EXP / "predictive_metrics_long.csv")
agg = p.groupby(["dataset", "condition"], as_index=False).agg(
    auprc=("auprc", "mean"), macro_f1=("macro_f1", "mean"),
    minority_f1=("minority_f1", "mean"), minority_recall=("minority_recall", "mean"),
    auroc=("auroc", "mean"), brier=("brier", "mean")
)
agg.to_csv(TABLE / "strengthened_augmentation_summary.csv", index=False)

order = ["Real only", "Random oversampling", "Random undersampling", "SMOTE", "Class weighting",
         "Standard CTGAN", "SepAware CTGAN", "Standard TVAE", "SepAware TVAE"]
lines = ["\\begin{tabular}{llrrrr}", "\\toprule", "Dataset & Method & AUPRC & Macro-F1 & Minority F1 & Brier \\\\", "\\midrule"]
for dataset in ["COVID-19", "Vigitel"]:
    subset = agg[agg.dataset == dataset].set_index("condition")
    for i, condition in enumerate(order):
        row = subset.loc[condition]
        label = dataset if i == 0 else ""
        lines.append(f"{label} & {condition} & {row.auprc:.3f} & {row.macro_f1:.3f} & {row.minority_f1:.3f} & {row.brier:.3f} \\\\")
    if dataset == "COVID-19":
        lines.append("\\midrule")
lines.extend(["\\bottomrule", "\\end{tabular}"])
(TABLE / "strengthened_augmentation_summary.tex").write_text("\n".join(lines))

d = pd.read_csv(EXP / "synthetic_diagnostics_long.csv")
diag = d.groupby(["dataset", "condition"], as_index=False).agg(
    coverage=("minority_coverage_distance", "mean"), diversity=("minority_diversity", "mean"),
    exact_match=("exact_match_rate", "mean"), membership_auc=("membership_auc", "mean")
)
diag.to_csv(TABLE / "synthetic_diagnostics_summary.csv", index=False)

paired = []
for dataset in p.dataset.unique():
    for generator in ("CTGAN", "TVAE"):
        for metric in ("auprc", "macro_f1"):
            keys = ["repeat", "fold", "classifier"]
            standard = p[(p.dataset == dataset) & (p.condition == f"Standard {generator}")][keys + [metric]]
            selected = p[(p.dataset == dataset) & (p.condition == f"SepAware {generator}")][keys + [metric]]
            joined = selected.merge(standard, on=keys, suffixes=("_sep", "_standard"))
            delta = joined[f"{metric}_sep"] - joined[f"{metric}_standard"]
            half = t.ppf(.975, len(delta) - 1) * delta.std(ddof=1) / np.sqrt(len(delta))
            paired.append({"dataset": dataset, "generator": generator, "metric": metric,
                           "mean_delta": delta.mean(), "lower": delta.mean() - half,
                           "upper": delta.mean() + half, "n": len(delta)})
paired = pd.DataFrame(paired)
paired.to_csv(TABLE / "paired_sepaware_generator_differences.csv", index=False)

plot = paired[paired.metric == "auprc"].copy()
fig, ax = plt.subplots(figsize=(6.8, 3.8))
positions = np.arange(len(plot))
ax.errorbar(plot.mean_delta, positions,
            xerr=[plot.mean_delta - plot.lower, plot.upper - plot.mean_delta], fmt="o", capsize=4, color="#175a8a")
ax.axvline(0, color="black", lw=1, ls="--")
ax.set_yticks(positions, [f"{d} / {g}" for d, g in zip(plot.dataset, plot.generator)])
ax.set_xlabel("Paired AUPRC difference: SepAware minus standard generator")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(FIG / "strengthened_paired_auprc.png", dpi=300)
plt.close(fig)

controlled = EXP / "controlled_overlap_prevalence_summary.csv"
if controlled.exists():
    c = pd.read_csv(controlled)
    focus = c[(c.classifier == "LogisticRegression") & c.method.isin(["SMOTE", "SepAware-SMOTE"])].copy()
    pivot = focus.pivot_table(index=["prevalence", "class_sep", "overlap"], columns="method", values="auprc_mean").reset_index()
    pivot["gain"] = pivot["SepAware-SMOTE"] - pivot["SMOTE"]
    pivot.to_csv(TABLE / "controlled_sepaware_smote_gain.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    sns.lineplot(data=pivot, x="class_sep", y="gain", hue="prevalence", marker="o", palette="viridis", ax=ax)
    ax.axhline(0, color="black", lw=1, ls="--")
    ax.set_xlabel("Class separation (higher means less overlap)")
    ax.set_ylabel("AUPRC difference: SepAware-SMOTE minus SMOTE")
    fig.tight_layout()
    fig.savefig(FIG / "controlled_overlap_gain.png", dpi=300)
    plt.close(fig)

print(agg.to_string(index=False))
