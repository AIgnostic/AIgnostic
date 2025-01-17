import numpy as np
import pandas as pd
from folktables import ACSDataSource, ACSPublicCoverage
from autogluon.tabular import TabularPredictor
from sklearn.model_selection import train_test_split
import torch
import pickle
import os
import shutil

if __name__ == '__main__':

    save_dir = "./test_model_pkl/"
    temp_dir = "./huggingface_model/"

    os.makedirs(save_dir, exist_ok=True)

    # Check if GPU is available
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print("CUDA is available. Using GPU.")
    else:
        device = torch.device('cpu')
        print("CUDA is not available. Using CPU.")

    subsample_size = 5000
    data_source = ACSDataSource(survey_year='2018', horizon='1-Year', survey='person')
    acs_data = data_source.get_data(states=["CA"], download=True)

    features, label, group = ACSPublicCoverage.df_to_numpy(acs_data)

    X_train, X_test, y_train, y_test = train_test_split(
        features, 
        label, 
        test_size=0.2, 
        random_state=42
    )

    print("X_train shape:", X_train.shape)
    print("y_train shape:", y_train.shape)

    # Combine features + label into a single DataFrame for training
    train_data = np.column_stack((X_train, y_train))
    train_data = pd.DataFrame(train_data)

    # Subsample training data (helps avoid out-of-memory errors with TabPFN)
    if subsample_size is not None and subsample_size < len(train_data):
        train_data = train_data.sample(n=subsample_size, random_state=0)

    # Combine features + label into a single DataFrame for testing
    test_data = np.column_stack((X_test, y_test))
    test_data = pd.DataFrame(test_data)

    # Ensure device uses GPU if available, otherwise CPU
    # Also ensure num_gpus=1 only if device is 'cuda', else 0.
    use_gpu = 1 if device.type == 'cuda' else 0

    tabpfnmix_default = {
        "model_path_classifier": "autogluon/tabpfn-mix-1.0-classifier",
        "max_epochs": 10,
        "device": device.type,    
        "ag_args_fit": {
            "num_gpus": use_gpu,    # Force usage of GPU if available
        }
    }


    hyperparameters = {
        "TABPFNMIX": [
            tabpfnmix_default,
        ],
    }


    label = 19

    predictor = TabularPredictor(label=label, path=temp_dir)
    predictor = predictor.fit(
        train_data=train_data,
        hyperparameters=hyperparameters,
        verbosity=3,
    )


    with open("./test_model_pkl/huggingface_test_model.pkl", "wb") as f:
        pickle.dump(predictor, f)

    print(f"Model pickled and saved to {save_dir}.")

