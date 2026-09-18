import numpy as np
import pandas as pd

from sepaware.selection import SelectionConfig, robust_unit, score_candidates, select_by_quota


def test_robust_unit_range_and_zero_scale():
    assert np.allclose(robust_unit([2, 2, 2]), 0.5)
    values = robust_unit([0, 1, 2, 100])
    assert np.all((0 <= values) & (values <= 1))


def test_selection_is_deterministic_and_respects_quota():
    real = pd.DataFrame({"x": [0.0, 0.2, 1.0, 1.2], "c": [0, 0, 1, 1], "y": [0, 0, 1, 1]})
    pool = pd.DataFrame({"x": [0.1, 0.9, 1.1], "c": [0, 1, 1], "y": [0, 1, 1]})
    scored = score_candidates(pool, real, features=["x", "c"], numerical=["x"], categorical=["c"], target="y", seed=7, config=SelectionConfig())
    one = select_by_quota(scored, "y", {1: 1})
    two = select_by_quota(scored, "y", {1: 1})
    assert one.candidate_index.tolist() == two.candidate_index.tolist()
    assert one.y.tolist() == [1]
