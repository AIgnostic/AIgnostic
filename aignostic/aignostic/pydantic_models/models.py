from pydantic import BaseModel
import pandas as pd

class DataSet(BaseModel):
    columns: dict

class QueryOutput(BaseModel):
    columns: dict

def to_dataframe(dataset: DataSet) -> pd.DataFrame:
    """
    Convert a pydantic dataset to a pandas dataframe
    """
    return pd.DataFrame(columns=dataset.columns)
