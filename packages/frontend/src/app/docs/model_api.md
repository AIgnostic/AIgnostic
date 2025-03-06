# How do I create a Model API for the model I wish to evaluate?

If you are using the Production version of AIgnostic (i.e. hosted on https://aignostic.docsoc.co.uk) then you will need to be hosting your API endpoint on a URL on the public internet in order for AIgnostic to interface with it. If you are using the local deployment (i.e. running AIgnostic on localhost via ```./aignostic.py run```) then you can use locally hosted servers for your APIs.

The Model API takes in `{features : List[List], labels: List[List], groups: List}`
and should return a List of labels 

```python
@app.post("/predict")
def predict(dataset: DataSet) -> DataSet:
    """
    Given a dataset, predict the expected outputs for the model
    """
    # Return identical dataframe for now - fill this in with actual test models when trained
    out: np.ndarray = model.predict(dataset.rows)
    rows: list[list] = out.tolist() if len(dataset.rows) > 1 else [out.tolist()]
    return DataSet(column_names=dataset.column_names, rows=rows)
