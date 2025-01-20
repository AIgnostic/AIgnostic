from typing import Any, Dict, List
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
