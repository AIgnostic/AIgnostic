# How do I create a Dataset API for the dataset I wish to evaluate?

The Dataset API should expose a "/fetch-datapoints" GET endpoint.

An important assumption that our metrics make is that the data obtained is independent and identically distributes (i.i.d.).
Therefore please ensure that your dataset is as such, and that it returns a batch of such random samples.

```python
@app.get('/fetch-datapoints')
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

        acs_datapoints = pd.concat([features.iloc[indices], label.iloc[indices]], axis=1)
        acs_datapoints = acs_datapoints.replace({
            pd.NA: None,
            np.nan: None,
            float('inf'): None,
            float('-inf'): None
        })

        return JSONResponse(content=df_to_JSON(acs_datapoints), status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
