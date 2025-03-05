# How do I create a Dataset API for the dataset I wish to evaluate?

The Dataset API should expose a "/fetch-datapoints" GET endpoint.

An important assumption that our metrics make is that the data obtained is independent and identically distributes (i.i.d.).
Therefore please ensure that your dataset is as such, and that it returns a batch of such random samples. The return type of fetch*datapoints is a `DatasetResponse` pydantic model. Since numpy types are not serialisable, you will need to convert them to a serialisable type. e.g. np.bool* types are converted to python bools in the example below.

```python
@app.get('/fetch-datapoints', dependencies=[Depends(get_dataset_api_key)], response_model=DatasetResponse)
async def fetch_datapoints(indices: list[int] = Body([0, 1])):
    """
    Given a list of indices, fetch the data at each index and convert into
    our expected JSON format, and returns it in a JSON response. Defaults to
    fetching the first row of the ACS data.

    Args:
        indices (list[int]): A list of indices to fetch from the ACS data.
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
