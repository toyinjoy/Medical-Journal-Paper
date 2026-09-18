import numpy as np

from sepaware.evaluation import predictive_metrics


def test_metric_directions_and_names():
    y = np.array([0, 0, 1, 1])
    good = predictive_metrics(y, np.array([0.1, 0.2, 0.8, 0.9]))
    bad = predictive_metrics(y, np.array([0.9, 0.8, 0.2, 0.1]))
    assert good["auprc"] > bad["auprc"]
    assert good["brier"] < bad["brier"]
    assert {"positive_f1", "positive_precision", "positive_recall"} <= set(good)
