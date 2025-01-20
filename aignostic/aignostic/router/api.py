from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, HTTPException


api = APIRouter()


class DatasetRequest(BaseModel):
    datasetURL: HttpUrl
    modelURL: HttpUrl
    metrics: list[str]


@api.post("/get_info")
async def get_info(request: DatasetRequest):
    """
    Frontend will post URLs, metrics, etc., as JSON to this endpoint.
    This function validates, processes, and forwards the data to the controller.
    """
    try:
        # Extract data from the validated request
        datasetURL = request.datasetURL
        modelURL = request.modelURL
        metrics = request.metrics

        print("Received request: ", datasetURL, modelURL, metrics)

        # # Example of processing or passing data to a controller
        # # Here you could make a request to the dataset API or perform metric calculations
        # result = {
        #     "api_url": api_url,
        #     "processed_metrics": [metric.upper() for metric in metrics],  # Example processing
        # }

        # return {"message": "Data successfully processed", "result": result}

        return {"message": "Data successfully received"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/")
def hello():
    return {"message": "Hello Worlds!"}


@api.get("/repeat/{text}")  # /repeat/hello, /repeat/a,
def repeat(text: str):
    return {"message": text}


class Request(BaseModel):  # class Request extends BaseModel
    text: str


@api.post("/echo")
def echo(request: Request):
    return {"message": request.text}
