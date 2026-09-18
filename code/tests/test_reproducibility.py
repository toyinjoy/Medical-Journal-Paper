import pandas as pd

from sepaware.selection import select_by_quota


def test_stable_candidate_index_breaks_score_ties():
    frame = pd.DataFrame({"target": [1, 1, 1], "score": [0.5, 0.5, 0.5], "candidate_index": [2, 0, 1]})
    selected = select_by_quota(frame, "target", {1: 2})
    assert selected.candidate_index.tolist() == [0, 1]
