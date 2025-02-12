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

from contextlib import asynccontextmanager
from common.rabbitmq.constants import RESULT_QUEUE
from fastapi import FastAPI, Response
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aggregator.rabbitmq import fastapi_connect_rabbitmq, channel


@asynccontextmanager
async def connect_rabbit_mq(app: FastAPI):
    channel, connection = fastapi_connect_rabbitmq()
    yield channel
    channel.close()
    connection.close()


aggregator_app = FastAPI(lifespan=connect_rabbit_mq)
# Add CORS middleware
aggregator_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MetricsAggregatedResponse(BaseModel):
    message: str = "Data successfully received"
    results: list[dict]


def fetch_result_from_queue():
    """
    Function to fetch a result from the result queue
    """

    method_frame, header_frame, body = channel.basic_get(
        queue=RESULT_QUEUE, auto_ack=True
    )
    if method_frame:
        result_data = json.loads(body)
        print(f"Received result: {result_data}")

        # TEMPORARY
        # Format the data into the format the frontend expects
        results = []
        if "error" in result_data:
            results.append({"error": result_data["error"]})
        else:
            for metric, value in result_data["metric_values"].items():
                results.append(
                    {
                        "metric": metric,
                        "result": value,
                        "legislation_results": ["Placeholder"],
                        "llm_model_summary": ["Placeholder"],
                    }
                )

        return results
    return None


@aggregator_app.get("/results")
def get_results() -> MetricsAggregatedResponse:
    """
    Endpoint to retrieve the results of the metrics calculation
    """
    # return MetricsAggregatedResponse(results=[])
    result = fetch_result_from_queue()
    if result:
        return MetricsAggregatedResponse(results=result)
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(aggregator_app, host="0.0.0.0", port=5002)
