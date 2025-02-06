"""
This is a (temporary) aggregator microservice implementation
Currently this service:
- exposes a /results endpoint to retrieve the results of the metrics calculation
- when this endpoint is hit, fetches a result from the result queue and returns it

In reality this service would:
- pick up results from the results queue and aggregate them
- until all results have been processed and aggregated
- and then return the aggregated results
Instead of polling an endpoint, there would instead be a socket connection
between the router and aggregator, allowing for real-time updates.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from aignostic.router.connection_constants import channel, RESULT_QUEUE
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

aggregator_app = FastAPI()
# Add CORS middleware
aggregator_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["GET"],  # Only allow GET requests if that's all you need
    allow_headers=["Content-Type", "Authorization"],  # Be explicit about required headers
)



class MetricsAggregatedResponse(BaseModel):
    message: str = "Data successfully received"
    results: list[dict]


def fetch_result_from_queue():
    """
    Function to fetch a result from the result queue
    """
    print("Before basic_get")
    method_frame, header_frame, body = channel.basic_get(queue=RESULT_QUEUE, auto_ack=True)

    if method_frame:
        try:
            print(f"Headers received: {header_frame}")
            print(f"Body (raw): {body}")
            result_data = json.loads(body.decode('utf-8'))
            print(f"Received result: {result_data}")

            # TEMPORARY
            # Format the data into the format the frontend expects
            results = []
            for metric, value in result_data["metric_values"].items():
                results.append({
                    "metric": metric,
                    "result": value,
                    "legislation_results": ["Placeholder"],
                    "llm_model_summary":  ["Placeholder"]
                })

            return results
        except json.JSONDecodeError as e:
            print(f"Error decoding result: {e}")
        except Exception as e:
            print(f"Unexpected error processing result: {e}")
    return None


@aggregator_app.get("/results", response_model=MetricsAggregatedResponse)
async def get_results():
    print("Fetching results")
    try:
        result = fetch_result_from_queue()
        if result:
            print(f"Final response data: {MetricsAggregatedResponse(results=result)}")
            return MetricsAggregatedResponse(results=result)
        return JSONResponse(content={"message": "No results available"}, status_code=204)
    except RuntimeError as e:
        return JSONResponse(content={"message": f"Error fetching results: {e}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(aggregator_app, host="0.0.0.0", port=5002)
