from typing import Any, Dict, List
from pydantic import BaseModel
import pandas as pd

class DataSet(BaseModel):
    columns: Dict[str, Any]  # A dictionary with string keys and values of any type

class QueryOutput(BaseModel):
    columns: Dict[str, Any]  # Generic dictionary to handle any data structure

def to_dataframe(dataset: DataSet) -> pd.DataFrame:
    """
    Convert a pydantic dataset to a pandas dataframe
    """
    return pd.DataFrame(columns=dataset.columns)

def to_dataset(data_input: str, file_type: str):
    """
    Convert a file to a pydantic dataset

    Args: 
        data_input (str): path to CSV or JSON file
        file_type (str): 'csv' or 'json'

    Returns:
        DataSet: A pydantic dataset object
    """

    if file_type == "csv":
        df = pd.read_csv(data_input)
    elif file_type == "json":   
        df = pd.read_json(data_input)
     
    else:
        raise ValueError("File type not supported. Please use 'csv' or 'json'")


    print("Dataframe")
    print(df)
  
    dataset = DataSet(columns={col: str(df[col].dtype) for col in df.columns})
    
    print("Generated Dataset Object:")
    print(dataset)

    return dataset

    
