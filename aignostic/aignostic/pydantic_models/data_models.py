from pydantic import BaseModel
from typing import List
import numpy as np
import pandas as pd


# TODO: Implement in validate_dataset_api.py endpoint
class ValidateDatasetRequest(BaseModel):
    """
    A model for a dataset to be validated

    Attributes:
        url: str - the URL of the dataset to be validated
    """
    url: str


class DataSet(BaseModel):
    """
    A model for a dataset to be sent over HTTP by JSON

    Attributes:
        column_names: List[str] - the names of the columns in the dataset
        rows: List[List] - the rows of the dataset
    """
    column_names: List[str]
    rows: List[List]


def df_to_JSON(df: pd.DataFrame) -> dict:
    """
    Convert a pandas dataframe to a JSON string in the required format
    """
    column_names: list = list(df.columns)
    rows: list[list] = list(list(r) for r in df.values)
    return {"column_names": column_names, "rows": rows}


def arr_to_JSON(arr: np.ndarray) -> dict:
    """
    Convert a pandas dataframe to a JSON string in the required format
    """
    column_names = None
    rows: list[list] = list(list(r) for r in arr)
    return {"column_names": column_names, "rows": rows}


def csv_to_JSON(file_path: str, header_row: bool = True) -> dict:
    """
    Convert a csv to a JSON string in the required format
    """
    import csv
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)

        header = None
        rows: list[list] = [[]]
        try:
            if header_row:
                header = next(csv_reader)
                header = [c.strip() for c in header]
            rows = [[value.strip() for value in row] for row in csv_reader]
            return {"column_names": header, "rows": rows}
        except StopIteration:
            return {"column_names": header, "rows": rows}
