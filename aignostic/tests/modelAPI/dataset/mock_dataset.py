from fastapi import FastAPI, HTTPException
import pandas as pd
import random
import os
from aignostic.dataset_loader.loader import DatasetLoader

app = FastAPI()

parent_dir = os.path.dirname(os.path.dirname(__file__))
csv_path = os.path.join(parent_dir, "dataset", "test.csv")
dataset_loader = DatasetLoader(dataset_path=csv_path, dataset_type="csv")


@app.get("/dataset")
def fetch_random_datapoint():
    """
    Fetch a random datapoint from the dataset, optionally applying filters.
    """
    data = dataset_loader.get_dataset()

    # Apply filters if needed (filter logic omitted for brevity)
    filtered_data = data

    if filtered_data.empty:
        raise HTTPException(status_code=404, detail="No matching datapoints found")

    random_index = random.randint(0, len(filtered_data) - 1)
    datapoint = filtered_data.iloc[random_index].to_dict()
    # Replace NaN with None in the datapoint
    cleaned_datapoint = {key: (value if pd.notna(value) else None) for key, value in datapoint.items()}
    return {"datapoint": cleaned_datapoint}
