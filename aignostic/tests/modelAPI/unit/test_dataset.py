from fastapi import FastAPI 
from fastapi.testclient import TestClient
from pydantic import BaseModel
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.models import DataSet, QueryOutput, to_dataframe, to_dataset
import logging
import os
from tests.modelAPI.dataset.mock_dataset import app as dataset_app


def test_to_dataframe(capsys):
    """
    Test the to_dataframe function
    """
    dataset = DataSet(columns={"a": "int", "b": "float"})
    df = to_dataframe(dataset)
    assert df.shape == (0, 2)
    assert df.columns.tolist() == ["a", "b"]
    with capsys.disabled():
        print("Dataframe:")
        print(df)

def test_to_dataset_json():
    """
    Test the to_dataset function with a JSON file
    """
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    json_path = os.path.join(parent_dir, "dataset", "test.json")
    if parent_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + parent_dir
    dataset = to_dataset(json_path, "json")


def test_to_dataset_csv():
    """
    Test the to_dataset function with a CSV file
    """
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(parent_dir, "dataset", "test.csv")
    if parent_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + parent_dir
    dataset = to_dataset(csv_path, "csv")



client_dataset = TestClient(dataset_app)

def test_dataset_fetch_api():
    """
    Test the dataset fetch API
    """
    response = client_dataset.get("/dataset")
    assert response.status_code == 200
    data = response.json()
    assert "datapoint" in data
    print(data)
