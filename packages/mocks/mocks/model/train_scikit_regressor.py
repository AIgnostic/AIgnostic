from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import pandas as pd
from mocks.dataset.boston_housing_data_server import (
    BOSTON_FEATURES as features,
    BOSTON_LABELS as labels
)

def main():
    print("Training a scikit-learn regression model...")
    boston = fetch_openml(name="boston", version=1, as_frame=True)
    df = boston.frame

    # Convert all columns to numeric type
    X = df[features].apply(pd.to_numeric, errors='coerce')
    y = pd.to_numeric(df[labels], errors='coerce')


    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # save the model
    filename: str = "scikit_regressor.sav"
    pickle.dump(model, open(filename, "wb"))
    print("Success! Model trained and saved!")


if __name__ == "__main__":
    main()