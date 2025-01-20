from pydantic import BaseModel
from typing import Optional, List, Union
import numpy as np
import pandas as pd

class Data(BaseModel):
    """
    A Pydantic model for a dataset to be sent over HTTP by JSON
      - column_names: Optional[List] - the names of the columns in the dataset
      - rows: List[List] - the rows of the dataset
    """
    column_names: Optional[List]
    rows: List[List]

def df_to_JSON(df: pd.DataFrame) -> dict:
    """
    Convert a pandas dataframe to a JSON string in the required format
    """
    column_names : list = list(df.columns)
    rows : list[list] = list(list(r) for r in df.values)
    return {"column_names": column_names, "rows": rows}

def arr_to_JSON(arr : np.array) -> dict:
    """
    Convert a pandas dataframe to a JSON string in the required format
    """
    column_names = None
    rows = list(list(r) for r in arr)

def csv_to_JSON(file_path : str, header_row : bool = True) -> dict:
    """
    Convert a csv to a JSON string in the required format
    """
    import csv
    with open(file_path, 'r', newline='\n') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(list(row) for row in reader)
        if header_row:
            column_names = list(next(reader))
            return {"column_names": column_names, "rows": rows}
        return {"column_names": None, "rows": rows}

