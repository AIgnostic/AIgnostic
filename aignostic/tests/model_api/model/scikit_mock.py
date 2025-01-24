from fastapi import FastAPI
import numpy as np
from sklearn.pipeline import Pipeline
import pickle
from aignostic.pydantic_models.data_models import DataSet, ModelResponse
import os#
import logging
from fastapi.responses import JSONResponse

app = FastAPI()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model: Pipeline = pickle.load(open(os.path.join(os.path.dirname(__file__), '../../../scikit_model.sav'), 'rb'))

@app.post("/predict")
def predict(dataset: DataSet) -> ModelResponse:
    """
    Given a dataset, predict the expected outputs for the model
    """
    try : 
        out = []
        for feature in dataset.features:
            lol = model.predict(np.array([feature]))
            out.append(lol.astype(str))
        out = [pred.tolist() for pred in out]
        return JSONResponse(content={"predictions": dataset.labels}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



"""
TODO: (Low Priority) Extend to batch querying / single datapoint querying for convenience
(e.g. if dataset is very large)
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5001)
