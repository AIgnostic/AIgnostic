# How do I create an API endpoint for the Model I wish to evaluate?

If you are using the Production version of AIgnostic (i.e. hosted on https://aignostic.docsoc.co.uk) then you will need to be hosting your API endpoint on a URL on the public internet in order for AIgnostic to interface with it. If you are using the local deployment (i.e. running AIgnostic on localhost via ```./aignostic.py run```) then you can use locally hosted servers for your APIs.

The model API should expose a '/predict' POST endpoint, which expects model input to be in the format of

```python
class ModelRequest():
    "features": List[List]
    "labels": List[List]
    "groups": Optional[List]
```

and should return a List of predictions and, optionally, confidence scores (some metrics require this).

```python
class ModelResponse():
    "predictions": List[List]
    "confidence_scores": Optional[List[List]]
```


#### Example Model API endpoint

```python
@app.post("/predict")
def predict(request: ModelRequest) ->  ModelResponse:
    """
    Given features, labels and groups, predict the expected outputs for the model
    """
    predictions, confidence_scores = model.predict(request)
    
    return ModelResponse(predictions=predictions, confidence_scores=confidence_scores)
```
