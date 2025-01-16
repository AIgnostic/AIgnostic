import numpy as np
from folktables import ACSIncome
from autogluon.tabular import TabularPredictor


if __name__ == '__main__':  
    train_data = pd.read_csv('https://autogluon.s3.amazonaws.com/datasets/Inc/train.csv')
    subsample_size = 5000
    if subsample_size is not None and subsample_size < len(train_data):
        train_data = train_data.sample(n=subsample_size, random_state=0)
    test_data = pd.read_csv('https://autogluon.s3.amazonaws.com/datasets/Inc/test.csv')

    tabpfnmix_default = {
        "model_path_classifier": "autogluon/tabpfn-mix-1.0-classifier",
        "model_path_regressor": "autogluon/tabpfn-mix-1.0-regressor",
        "n_ensembles": 1,
        "max_epochs": 30,
    }

    hyperparameters = {
        "TABPFNMIX": [
            tabpfnmix_default,
        ],
    }

    label = "age"
    problem_type = "regression"

    predictor = TabularPredictor(
        label=label,
        problem_type=problem_type,
    )
    predictor = predictor.fit(
        train_data=train_data,
        hyperparameters=hyperparameters,
        verbosity=3,
    )

    predictor.leaderboard(test_data, display=True)
