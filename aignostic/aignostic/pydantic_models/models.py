from pydantic import BaseModel
import numpy as np

class DataSet(BaseModel):
    data: np.ndarray

class QueryOutput(BaseModel):
    data: np.ndarray
