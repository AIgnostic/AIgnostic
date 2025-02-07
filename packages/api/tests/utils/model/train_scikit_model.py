from folktables import ACSDataSource, ACSEmployment  # type: ignore
import pandas as pd
from sklearn.linear_model import LogisticRegression  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.pipeline import make_pipeline, Pipeline  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
import pickle

"""
Create a basic scikit regression model - ignoring proper preprocessing as this is only for testing the API mock
"""


def main():
    # Import the folktables dataset and load the employment data
    data_source: ACSDataSource = ACSDataSource(
        survey_year="2018", horizon="1-Year", survey="person"
    )
    acs_data: pd.DataFrame = data_source.get_data(states=["AL"], download=True)
    features, label, group = ACSEmployment.df_to_numpy(acs_data)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test, group_train, group_test = train_test_split(
        features, label, group, test_size=0.2, random_state=0
    )

    # Train the model using logistic regression and preprocess with standard scaling
    model: Pipeline = make_pipeline(StandardScaler(), LogisticRegression())
    model.fit(X_train, y_train)

    # save the model
    filename: str = "scikit_model.sav"
    pickle.dump(model, open(filename, "wb"))
    print("Success! Model trained and saved!")


if __name__ == "__main__":
    main()
