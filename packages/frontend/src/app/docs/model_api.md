# How do I create an API endpoint for the Model I wish to evaluate?

The model API should expose a '/predict' POST endpoint, which expects model input to be in the format of

```python
class ModelRequest():
    "features": List[List]
    "labels": List[List]
    "groups": List
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
