from __future__ import annotations

import numpy as np
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score


def calibration_parameters(y_true, probability) -> tuple[float, float]:
    probability = np.clip(np.asarray(probability, float), 1e-6, 1 - 1e-6)
    x = logit(probability).reshape(-1, 1)
    model = LogisticRegression(C=1e6, max_iter=2000, solver="lbfgs").fit(x, np.asarray(y_true, int))
    return float(model.intercept_[0]), float(model.coef_[0, 0])


def predictive_metrics(y_true, probability, threshold: float = 0.5) -> dict[str, float]:
    y = np.asarray(y_true, int)
    p = np.asarray(probability, float)
    prediction = (p >= threshold).astype(int)
    intercept, slope = calibration_parameters(y, p)
    return {
        "auprc": average_precision_score(y, p),
        "auroc": roc_auc_score(y, p),
        "macro_f1": f1_score(y, prediction, average="macro", zero_division=0),
        "positive_f1": f1_score(y, prediction, pos_label=1, zero_division=0),
        "positive_precision": precision_score(y, prediction, pos_label=1, zero_division=0),
        "positive_recall": recall_score(y, prediction, pos_label=1, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y, prediction),
        "brier": brier_score_loss(y, p),
        "calibration_intercept": intercept,
        "calibration_slope": slope,
    }
