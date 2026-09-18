import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer


def test_imputer_statistics_come_only_from_training_fold():
    train = pd.DataFrame({"x": [0.0, np.nan, 2.0]})
    test = pd.DataFrame({"x": [1000.0, np.nan]})
    imputer = SimpleImputer(strategy="median").fit(train)
    assert imputer.statistics_[0] == 1.0
    assert imputer.transform(test)[1, 0] == 1.0
