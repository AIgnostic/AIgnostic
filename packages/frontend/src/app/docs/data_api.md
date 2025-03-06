# How do I create an API endpoint for the Dataset I wish to evaluate?

The Dataset API should expose a '/fetch-datapoints' GET endpoint, which expects a query parameter to specify the number of datapoints to fetch. The endpoint should return a JSON response containing the features, labels, and group IDs for the fetched datapoints, in the format below:

```python
class DatasetResponse(BaseModel):
    features: List[List]  # Each row corresponds to one datapoint. Each column is a feature.
    labels: List[List]  # Each row is a datapoint. Each column is a prediction feature.
    groups: List[int]  # Each row corresponds to the group ID of the datapoint at that index
```

Features and labels are mandatory inputs for prediction. The current version only contains metrics for single outputs (only one label), so the labels will look like a list of singleton lists. e.g. 'labels=[['positive'], ['positive'], ['negative]]' or 'labels=[[1], [2], [1]]' etc. It is defined as a 2D list for extensibility in the future for models with multiple outputs.

Group IDs is an optional field, though it is required for certain metrics, including many binary classification fairness metrics.

#

If you are using the Production version of AIgnostic (i.e. hosted on https://aignostic.docsoc.co.uk) then you will need to be hosting your API endpoint on a URL on the public internet in order for AIgnostic to interface with it. If you are using the local deployment (i.e. running AIgnostic on localhost via './aignostic.py run') then you can use locally hosted servers for your APIs.

An important assumption that our metrics make is that the data obtained is independent and identically distributed (i.i.d.).

#

Ensure that your dataset is independent and identically distributed (i.i.d.) and that it returns a batch of random samples. The 'fetch_datapoints' function returns a 'ModelInput' Pydantic model. Since NumPy types are not serializable, you need to convert them to a serializable type. For example, 'np.bool_' types are converted to Python 'bool' types in the example below.

```python
@app.get('/fetch-datapoints', response_model=DatasetResponse)
async def fetch_datapoints(num_datapoints: int = Query(alias="n")):
    """
    Given a list of indices, fetch the data at each index and convert into
    our expected JSON format, and returns it in a JSON response. Defaults to
    fetching the first row of the ACS data.

    Args:
        num_datapoints (int): The number of datapoints to fetch.
    Returns:
        JSONResponse: A JSON response containing the random datapoints.
    """
    try:
        filtered_features = features.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
            })
        filtered_labels = label.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
            })
        filtered_group_ids = group.iloc[indices].replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
            })

        filtered_features = list(list(r) for r in filtered_features.values)
        filtered_labels = [[(bool(r) if isinstance(r, np.bool_) else r for r in row)] for row in filtered_labels.values]
        filtered_group_ids = list(filtered_group_ids.values)

        return DatasetResponse(
            features=filtered_features,
            labels=filtered_labels,
            group_ids=filtered_group_ids
        )
    except Exception as e:
        return HTTPException(detail=f"error: {e}", status_code=500)
```
