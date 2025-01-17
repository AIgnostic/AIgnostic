## Model API (to be inputted by user)
The mock.py class shows the API format expected from the user when entering their model API to the system.

The `predict` method (can be renamed internally) and follows from the `/predict` endpoint. This endpoint receives data as an input in the form of a list of dictionaries, representing the contents of a pandas dataframe and expects an output of the same type for the predictions made by the model.