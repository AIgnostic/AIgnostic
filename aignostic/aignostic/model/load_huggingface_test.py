
import numpy as np
import pandas as pd
import pickle
from folktables import ACSDataSource, ACSPublicCoverage

if __name__ == '__main__':
    with open("./test_model_pkl/huggingface_test_model.pkl", "rb") as f:
        predictor = pickle.load(f)

    print("Model successfully loaded from pickle.")

    data_source = ACSDataSource(survey_year='2019', horizon='1-Year', survey='person')
    acs_data = data_source.get_data(states=["CA"], download=True)

    features, label, group = ACSPublicCoverage.df_to_numpy(acs_data)

    test_data = np.column_stack((features, label))
    test_data = pd.DataFrame(test_data)

    print(test_data.head())


    # Make predictions
    predictions = predictor.predict(test_data.drop(columns=19))

    print("Predictions:")
    print(predictions)

    # Evaluate the model
    evaluation_results = predictor.evaluate(test_data)

    print("Evaluation Results:")
    print(evaluation_results)
