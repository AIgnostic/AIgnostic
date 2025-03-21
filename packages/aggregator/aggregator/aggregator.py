import os
import json
import threading
import queue
import requests
import websockets.sync.server
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
from common.rabbitmq.constants import RESULT_QUEUE
import time
from common.models import (
    AggregatorMessage,
    MessageType,
    JobType,
    AggregatorJob,
    WorkerError,
    LegislationList,
)
from metrics.models import MetricValue, WorkerResults, MetricsPackageExceptionModel
from report_generation.utils import get_legislation_extracts, add_llm_insights
from worker.worker import USER_METRIC_SERVER_URL
from aggregator.connection_manager import ConnectionManager
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from .utils import (
    LEGISLATION_INFORMATION,
    filter_legislation_information,
    userLegislation,
    LegRequest,
)


manager = ConnectionManager()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Welcome to the Aggregator Service"}


@app.get("/fetch-frontend-information")
def fetch_frontend_information():
    try:
        labels = []
        for legislation in LEGISLATION_INFORMATION.values():
            labels.append(legislation.name)
        print("Labels", labels)
        return LegislationList(legislation=labels)
    except Exception as e:
        return {"error": str(e)}  # TODO: Catch the error


@app.post("/upload-selected-legislation")
async def upload_selected_legislation(request: LegRequest):
    try:
        legislation_list = request.legislation
        selected_legislation = filter_legislation_information(legislation_list)
        userLegislation[request.user_id] = selected_legislation
    except Exception as e:
        print(f"Uploading legislation errored: {e}")
        return {"error": str(e)}


def aggregator_metrics_completion_log():
    return AggregatorMessage(
        messageType=MessageType.METRICS_COMPLETE,
        message="Metrics processing complete - all batches successfully processed",
        statusCode=200,
        content=None,
    )


def aggregator_error_log(error):
    return AggregatorMessage(
        messageType=MessageType.ERROR,
        message="Error processing metrics",
        statusCode=500,
        content=error,
    )


def aggregator_final_report_log(report):
    return AggregatorMessage(
        messageType=MessageType.REPORT,
        message="Final report successfully generated",
        statusCode=200,
        content=report,
    )


def aggregator_intermediate_metrics_log(metrics):
    return AggregatorMessage(
        messageType=MessageType.METRICS_INTERMEDIATE,
        message="Batch successfully processed - intermediate metrics successfully generated",
        statusCode=202,
        content={"metrics_results": metrics},
    )


class MetricsAggregator:
    def __init__(self):
        self.metrics = {}
        self.samples_processed = 0
        self.total_sample_size = 0

    def set_total_sample_size(self, total_sample_size):
        self.total_sample_size = total_sample_size

    def aggregate_new_batch(self, batch_metrics_results, batch_size):
        for metric, metric_value_obj in batch_metrics_results.items():
            if metric not in self.metrics:
                # First time encountering this metric, initialize with the first batch value

                if isinstance(metric_value_obj, MetricsPackageExceptionModel):
                    self.metrics[metric] = {
                        "value": None,
                        "ideal_value": None,
                        "range": None,
                        "count": batch_size,
                        "error": metric_value_obj.detail,
                    }
                    continue
                # otherwise of type MetricValue
                self.metrics[metric] = {
                    "value": metric_value_obj.computed_value,
                    "ideal_value": metric_value_obj.ideal_value,
                    "range": metric_value_obj.range,
                    "count": batch_size,
                    "error": None,
                }

            else:
                if self.metrics[metric]["error"]:
                    # If there was a previous error, skip update
                    self.metrics[metric]["count"] += batch_size
                    continue
                if isinstance(metric_value_obj, MetricsPackageExceptionModel):
                    self.metrics[metric] = {
                        "value": None,
                        "ideal_value": None,
                        "range": None,
                        "count": self.metrics[metric]["count"] + batch_size,
                        "error": metric_value_obj.detail,
                    }
                    continue

                # Update the running average incrementally
                prev_value = self.metrics[metric]["value"]
                prev_count = self.metrics[metric]["count"]

                # Compute new weighted average
                new_count = prev_count + batch_size
                new_value = (
                    prev_value * prev_count
                    + metric_value_obj.computed_value * batch_size
                ) / new_count
                self.metrics[metric]["value"] = new_value
                self.metrics[metric]["count"] = new_count  # Update the total count

        self.samples_processed += batch_size

    def get_aggregated_metrics(self):
        """
        Returns the aggregated metrics as a dictionary.
        Example:
        {
            "metric1": {
                "value": value1,
                "ideal_value": ideal_value1,
                "range": range1
            },
            "metric2": {
                "value": value2,
                "ideal_value": ideal_value2,
                "range": range2
            },
            ...
        }
        """
        return self.metrics

        # results = {}
        # for metric, data in self.metrics.items():
        #     results[metric] = {
        #         "value": data["value"],
        #         "ideal_value": data["ideal_value"],
        #         "range": data["range"]
        #     }
        # return results


class ResultsConsumer:

    def __init__(self, host="localhost"):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        """

        self._host = host
        self._connection = None
        self._channel = None

    def connect(self):
        """Connect to RabbitMQ, returning the connection handle.

        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        self._connection = connect_to_rabbitmq(host=self._host)
        self._channel = self._connection.channel()
        init_queues(self._channel)

    def run(self, on_message_callback=None):
        """
        Run the consumer loop.

        """
        self.connect()
        try:
            self._channel.basic_consume(
                queue=RESULT_QUEUE,
                on_message_callback=on_message_callback,
                auto_ack=True,
            )
            print("Waiting for messages...")
            self._channel.start_consuming()  # Blocking call, waits for messages
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """
        Cleanly shutdown the connection to RabbitMQ.

        """
        print("Closing connection...")
        self._channel.close()
        self._connection.close()


RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
# Store messages until a client connects
message_queue = queue.Queue()
# user_id -> MetricsAggregator
user_aggregators: dict = {}


def process_batch_result(worker_results: WorkerResults, user_id: str):
    """Handles batch results from worker i.e. aggregating intermediate metric results"""
    print(f"Received result for user {user_id}: {worker_results}")

    if worker_results.user_defined_metrics is not None:
        print(
            f"User-defined metrics received for user {user_id}: {worker_results.user_defined_metrics}"
        )

    # ensure a metricsaffregator exists for the user
    if user_id not in user_aggregators:
        user_aggregators[user_id] = MetricsAggregator()

    aggregator: MetricsAggregator = user_aggregators[user_id]

    if aggregator.total_sample_size == 0:
        aggregator.set_total_sample_size(worker_results.total_sample_size)

    batch_metrics = worker_results.metric_values
    if worker_results.user_defined_metrics is not None:
        for metric, metric_value in worker_results.user_defined_metrics.items():

            metric_value_obj = (
                MetricsPackageExceptionModel(
                    detail=metric_value["error"],
                    status_code=metric_value["status_code"],
                )
                if "error" in metric_value
                else MetricValue(**metric_value)
            )
            batch_metrics[metric] = metric_value_obj

    aggregator.aggregate_new_batch(
        worker_results.metric_values, worker_results.batch_size
    )

    aggregates = aggregator.get_aggregated_metrics()
    # send the intermediate metrics to the user
    manager.send_to_user(user_id, aggregator_intermediate_metrics_log(aggregates))
    print(
        f"{aggregator.samples_processed} / {aggregator.total_sample_size} Processed for user {user_id}"
    )

    # if all batches have been processed, send final result

    if aggregator.samples_processed == aggregator.total_sample_size:
        print(f"Finished processing all batches for user {user_id}")

        # clear the user metric server :
        try:
            clear_response = requests.delete(
                f"{USER_METRIC_SERVER_URL}/clear-user-data/{worker_results.user_id}"
            )
            clear_response.raise_for_status()
            print(f"Clear response: {clear_response}")
        except Exception as e:
            print(f"Error clearing user data: {e}")

        print("Creating and sending final report")
        manager.send_to_user(
            user_id,
            AggregatorMessage(
                messageType=MessageType.LOG,
                message="Generating final report - this may take a few minutes",
                statusCode=200,
                content=None,
            ),
        )

        # send completion message
        manager.send_to_user(user_id, aggregator_metrics_completion_log())

        # send report
        report_thread = threading.Thread(
            target=generate_and_send_report, args=(user_id, aggregates, aggregator)
        )
        report_thread.start()

        # cleanup completed aggregator
        del user_aggregators[user_id]


def process_error_result(error_data: WorkerError, user_id: str):
    """Handles error results from worker"""
    manager.send_to_user(user_id, aggregator_error_log(error_data.error_message))


def get_api_key():
    # if GOOGLE_API_KEY_FILE is set, read the key from the file
    if os.getenv("GOOGLE_API_KEY_FILE"):
        with open(os.getenv("GOOGLE_API_KEY_FILE")) as f:
            return f.read().strip()
    return os.getenv("GOOGLE_API_KEY")


def aggregator_generate_report(user_id, aggregates, aggregator):
    """
    Generates a report to send to the frontend
    By collating the metrics, and pulling information from the report generator
    """
    print("Fetching Legislation Extracts")
    manager.send_to_user(
        user_id,
        AggregatorMessage(
            messageType=MessageType.LOG,
            message="Fetching Legislation Extracts",
            statusCode=200,
            content=None,
        ),
    )

    leg = LEGISLATION_INFORMATION

    if user_id in userLegislation:
        leg = userLegislation[user_id]

    report_properties_section = get_legislation_extracts(aggregates, leg)
    print("Adding LLM Insights")
    manager.send_to_user(
        user_id,
        AggregatorMessage(
            messageType=MessageType.LOG,
            message="Adding LLM Insights",
            statusCode=200,
            content=None,
        ),
    )
    report_properties_section = add_llm_insights(
        report_properties_section, get_api_key()
    )

    manager.send_to_user(
        user_id,
        AggregatorMessage(
            messageType=MessageType.LOG,
            message="Added LLM Insights. Sending final report...",
            statusCode=200,
            content=None,
        ),
    )
    report_info_section = {
        # TODO: Update with codecarbon info and calls to model from metrics
        "calls_to_model": aggregator.total_sample_size,
        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    }
    report_json = {"properties": report_properties_section, "info": report_info_section}
    return report_json


def generate_and_send_report(user_id, aggregates, aggregator):
    """Generates the report and sends it without blocking the main process."""
    try:
        report_json = aggregator_generate_report(user_id, aggregates, aggregator)
        manager.send_to_user(user_id, aggregator_final_report_log(report_json))
    except Exception as e:
        print(f"Error generating report for user {user_id}: {e}")
        manager.send_to_user(user_id, aggregator_error_log(str(e)))


def on_result_fetched(ch, method, properties, body):
    body = json.loads(body)
    job = AggregatorJob(**body)

    print(f"Received job of type {job.job_type}: {job}")

    if job.job_type == JobType.RESULT:
        process_batch_result(worker_results=job.content, user_id=job.user_id)
    elif job.job_type == JobType.ERROR:
        process_error_result(error_data=job.content, user_id=job.user_id)
    else:
        raise ValueError(f"Invalid job type: {job.job_type}")


def websocket_handler(websocket):
    """Handles incoming WebSocket connections."""
    try:
        user_id = websocket.recv()
        print(f"User {user_id} connected via websocket")

        # register this user
        manager.connect(user_id, websocket)

        for _ in websocket:
            # keep connection open
            pass
    except Exception as e:
        print(f"Websocket connection closed: {e}")
    finally:
        print(f"User {user_id} disconnected")
        manager.disconnect(user_id)


def start_websocket_server():
    server = websockets.sync.server.serve(websocket_handler, "0.0.0.0", 5005)
    print("WebSocket server started on ws://0.0.0.0:5005")
    server.serve_forever()  # Blocking call


def start_http_server():
    uvicorn.run(app, host="0.0.0.0", port=8005)
    print("HTTP server started on ws://0.0.0.0:8005")


if __name__ == "__main__":
    # Load environment variables

    from dotenv import load_dotenv

    load_dotenv()

    # Start WebSocket server in a separate thread
    threading.Thread(target=start_websocket_server, daemon=True).start()

    # Start HTTPs server in a separate thread
    threading.Thread(target=start_http_server, daemon=True).start()

    # Start RabbitMQ consumer (blocking)
    consumer = ResultsConsumer(RABBIT_MQ_HOST)
    consumer.run(on_result_fetched)
