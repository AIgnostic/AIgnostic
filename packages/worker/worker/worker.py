"""
This file contains the script that a worker runs to process jobs on the job queue
Each worker:
- Fetches a job (containing a batch size and a list of metrics to compute)
- Fetches the data from the data URL
- Fetches the model from the model URL
- Computes the metrics
- Puts the results on a results queue
"""

import os
import json
import asyncio
import random
import threading
from common.models.pipeline import Batch, JobStatus, JobStatusMessage
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues, publish_to_queue
from metrics.models import WorkerResults, convert_calculate_request_to_dict
import requests
from pydantic.networks import HttpUrl
import metrics.metrics as metrics_lib
from common.models import (
    CalculateRequest,
    DatasetResponse,
    ModelResponse,
    AggregatorJob,
    JobType,
    WorkerError,
)
from common.rabbitmq.constants import BATCH_QUEUE, RESULT_QUEUE, STATUS_QUEUE
from metrics.models import WorkerException
from pydantic import ValidationError

from pika.adapters.blocking_connection import BlockingChannel
import re
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout


RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

USER_METRIC_SERVER_URL = os.environ.get(
    "USER_METRIC_SERVER_URL", "http://user-added-metrics:8010"
)


def convert_localhost_url(url: str) -> str:
    """
    Function to convert a URL to localhost if the URL is not localhost
    """
    pattern = re.compile(r"http://localhost:(\d+)/(\S*)")
    return pattern.sub(r"http://host.docker.internal:\1/\2", url)


class Worker:
    _channel: BlockingChannel

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
        """
        self._connection = connect_to_rabbitmq(host=self._host)
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()
        init_queues(self._channel)
        print("Connection established to RabbitMQ")

    def queue_result(self, result: WorkerResults, user_id: str):
        """
        Function to queue the results of a job
        """
        job = AggregatorJob(job_type=JobType.RESULT, user_id=user_id, content=result)

        self._channel = publish_to_queue(
            self._channel, RESULT_QUEUE, job.model_dump_json()
        )

    def queue_error(self, error: WorkerError, user_id: str):
        """
        Function to queue an error message
        """
        job = AggregatorJob(
            job_type=JobType.ERROR,
            user_id=user_id,
            content=error,
        )
        self._channel = publish_to_queue(
            self._channel, RESULT_QUEUE, job.model_dump_json()
        )

    def close(self):
        self._channel.close()

    def unpack_batch(self, data: str) -> Batch:
        batch_data = json.loads(data)
        print(f"Received job: {batch_data}")
        try:
            print("Unpacking batch data")
            return Batch(**batch_data)
        except ValueError as e:
            raise WorkerException(f"Invalid batch format: {e}", status_code=400)

    async def fetch_data(
        self, data_url: HttpUrl, dataset_api_key, batch_size: int
    ) -> DatasetResponse:
        """
        Helper function to fetch data from the dataset API.

        Params:
        - data_url : API URL of the dataset
        - dataset_api_key : API key for authentication
        - batch_size : Number of records to fetch
        """

        url = convert_localhost_url(str(data_url))
        headers = (
            {"Authorization": f"Bearer {dataset_api_key}"} if dataset_api_key else {}
        )
        params = {"n": batch_size}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            # Raise for HTTP errors (4xx, 5xx)
            response.raise_for_status()

        except ConnectionError as e:
            raise WorkerException(
                detail=f"Failed to connect to dataset API at {url}: {e}",
                status_code=503,
            )

        except Timeout as e:
            raise WorkerException(
                detail=f"Request to dataset API at {url} timed out: {e}",
                status_code=504,
            )

        except HTTPError as e:
            raise WorkerException(
                detail=f"HHTP Error on request to dataset API at {url}: {e}",
                status_code=response.status_code,
            )

        except RequestException as e:
            raise WorkerException(
                detail=f"An error occurred while contacting the dataset API: {e}",
                status_code=500,
            )

        except Exception as e:
            raise WorkerException(
                detail=f"An unknown error occurred while querying the model: {e}",
                status_code=500
            )

        try:
            # Ensure response is JSON
            if "application/json" not in response.headers.get("Content-Type", ""):
                raise WorkerException(
                    f"Unexpected response type from dataset API: {response.headers.get('Content-Type')}",
                    status_code=500,
                )

            dataset_response = DatasetResponse(**response.json())
            return dataset_response

        except ValidationError as e:
            raise WorkerException(
                f"Data error - Incorrect format from dataset API: \n{e}",
                status_code=500,
            )

        except Exception as e:
            raise WorkerException(
                f"Could not parse dataset response - {e}; response = {response.text}",
                status_code=500,
            )

    async def query_model(
        self, model_url: HttpUrl, data: DatasetResponse, model_api_key
    ) -> ModelResponse:
        """
        Helper function to query the model API

        Params:
        - modelURL : API URL of the model
        - data : Data to be passed to the model in JSON format with DataSet pydantic model type
        - modelAPIKey : API key for the model
        """
        url = convert_localhost_url(str(model_url))
        headers = {"Authorization": f"Bearer {model_api_key}"} if model_api_key else {}

        try:
            response = requests.post(
                url, json=data.model_dump(), headers=headers, timeout=90
            )

            # Raise for status (HTTPError for 4xx, 5xx)
            response.raise_for_status()

        except ConnectionError as e:
            raise WorkerException(
                detail=f"Failed to connect to model at {url}: {e}", status_code=503
            )

        except Timeout as e:
            raise WorkerException(
                detail=f"Request to model at {url} timed out: {e}", status_code=504
            )

        except HTTPError as e:
            raise WorkerException(
                detail=f"HHTP Error on request to dataset API at {url}: {e}",
                status_code=response.status_code,
            )

        except RequestException as e:
            raise WorkerException(
                detail=f"An error occurred while contacting the model: {e}",
                status_code=500,
            )

        except Exception as e:
            raise WorkerException(
                detail=f"An unknown error occurred while querying the model: {e}",
                status_code=500,
            )

        try:
            # Ensure response is JSON
            if "application/json" not in response.headers.get("Content-Type", ""):
                raise WorkerException(
                    f"Unexpected response type from model: {response.headers.get('Content-Type')}",
                    status_code=500,
                )

            model_response = ModelResponse(**response.json())
            self._check_model_response(model_response.predictions, data.labels)

            return model_response

        except Exception as e:
            raise WorkerException(
                f"Could not parse model response - {e}; response = {response.text}",
                status_code=500,
            )

    async def process_job(self, batch: Batch):

        print("Processing Job")

        metrics_data = batch.metrics

        try:
            # fetch data from datasetURL
            print("Fetching data")
            dataset_response = await self.fetch_data(
                data_url=metrics_data.data_url,
                dataset_api_key=metrics_data.data_api_key,
                batch_size=batch.batch_size,
            )
            print(f"Data fetched: {dataset_response}")
            # query model at modelURL
            # TODO: Separate model input and dataset output so labels and group IDs are not passed to the model
            # TODO: Refactor to use pydantic models
            model_response = await self.query_model(
                metrics_data.model_url,
                dataset_response,
                metrics_data.model_api_key,
            )

            true_labels = dataset_response.labels
            predicted_labels = model_response.predictions

            print(f"Metrics to compute: {metrics_data.metrics}")

            # some preprocessing for FinBERT
            # TODO: Need to sort out how to handle this properly
            if metrics_data.model_type == "binary_classification":
                predicted_labels, true_labels = self.binarize_finbert_output(
                    predicted_labels, true_labels
                )
            elif metrics_data.model_type == "multi_class_classification":
                predicted_labels, true_labels = self.convert_to_numeric_classes(
                    predicted_labels, true_labels
                )

            # Construct CalculateRequest
            metrics_request = CalculateRequest(
                metrics=metrics_data.metrics,
                batch_size=batch.batch_size,
                input_features=dataset_response.features,
                true_labels=true_labels,
                predicted_labels=predicted_labels,
                confidence_scores=model_response.confidence_scores,
                task_name=metrics_data.model_type,
                # TODO: Do this group stuff properly
                privileged_groups=[{"protected_attr": 1}],
                unprivileged_groups=[{"protected_attr": 0}],
                protected_attr=[random.randint(0, 1) for _ in range(len(true_labels))],
                model_url=convert_localhost_url(str(metrics_data.model_url)),
                model_api_key=metrics_data.model_api_key,
                total_sample_size=batch.total_sample_size,
                regression_flag=metrics_data.model_type == "regression",
            )

            # Calculate metrics
            metrics_results = metrics_lib.calculate_metrics(metrics_request)
            print(f"Final Results: {metrics_results}")
            # add user_id to the results
            worker_results = WorkerResults(
                **metrics_results.model_dump(),
                user_id=batch.job_id,
                user_defined_metrics=None,
            )

            # TODO: Add more robustness for server querying e.g. timeouts and retries
            try:
                # query the user metric server to get the user-defined metrics
                user_metrics_server_response = requests.get(
                    f"{USER_METRIC_SERVER_URL}/inspect-uploaded-functions/{batch.job_id}",
                )

                user_defined_metrics = []
                if user_metrics_server_response.status_code == 200:
                    user_defined_metrics = user_metrics_server_response.json()[
                        "functions"
                    ]
                    print(f"User defined metrics: {user_defined_metrics}")
                else:
                    print(
                        f"SERVER RESPONSE NOT OKAY: {user_metrics_server_response.text}"
                    )
            except Exception as e:
                print(f"Exception occurred while fetching user metrics: {e}")
                user_defined_metrics = []

            for metric in user_defined_metrics:
                try:
                    params_dict = convert_calculate_request_to_dict(metrics_request)
                    # execute the user-defined metric
                    exec_response = requests.post(
                        f"{USER_METRIC_SERVER_URL}/compute-metric",
                        json={
                            "user_id": batch.job_id,
                            "function_name": metric,
                            "params": params_dict,
                        },
                    )
                    if exec_response.status_code == 200:
                        result = exec_response.json()["result"]
                        print(f"User metric {metric} result: {result}")
                        if worker_results.user_defined_metrics is None:
                            worker_results.user_defined_metrics = {}
                        worker_results.user_defined_metrics[metric] = result
                    else:
                        print(f"SERVER RESPONSE NOT OKAY: {exec_response.text}")

                except Exception as e:
                    print(f"ERROR EXECUTING USER METRIC: {e}")

            if len(user_defined_metrics) != 0 or user_defined_metrics is not None:
                print(f"Final Results with user metrics: {worker_results}")
                try:
                    clear_response = requests.delete(
                        f"{USER_METRIC_SERVER_URL}/clear-user-data/{batch.job_id}"
                    )
                    print(f"Clear response: {clear_response}")
                except Exception as e:
                    print(f"Error clearing user data: {e}")

            self.queue_result(worker_results, batch.job_id)
            self.send_status_completed(batch.job_id, batch.batch_id)
            return
        except WorkerException as e:
            # known/caught error
            # should be sent back to user
            self.queue_error(
                WorkerError(error_message=e.detail, error_code=e.status_code),
                user_id=batch.job_id,
            )
            self.send_status_error(batch.job_id, batch.batch_id, e)
        except Exception as e:
            self.queue_error(
                WorkerError(error_message="An unknown error occurred", error_code=500),
                user_id=batch.job_id,
            )
            self.send_status_error(batch.job_id, batch.batch_id, e)

    def send_status_completed(self, job_id: str, batch_id: str):
        """
        Function to send a status message to the status queue
        """
        self._channel = publish_to_queue(
            self._channel,
            STATUS_QUEUE,
            JobStatusMessage(
                job_id=job_id, batch_id=batch_id, status=JobStatus.COMPLETED
            ).model_dump_json(),
        )

    def send_status_error(self, job_id: str, batch_id: str, error):
        """
        Function to send a status message to the status queue
        """
        self._channel = publish_to_queue(
            self._channel,
            STATUS_QUEUE,
            JobStatusMessage(
                job_id=job_id,
                batch_id=batch_id,
                status=JobStatus.ERRORED,
                errorMessage=str(error),
            ).model_dump_json(),
        )

    def run(self):
        self.connect()

        # Start event loop
        def start_event_loop(loop: asyncio.AbstractEventLoop) -> None:
            asyncio.set_event_loop(loop)
            loop.run_forever()

        # Create a new event to run batchs
        loop = asyncio.new_event_loop()

        # Start the loop in a new daemon thread
        thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
        thread.start()

        # Use asyncio.run_coroutine_threadsafe()
        def callback(channel, method, properties, body):
            print(" [x] Received %r" % body)
            print("[x] Unpacking batch")
            batch = self.unpack_batch(body)
            print("[x] Processing batch...")
            task = asyncio.run_coroutine_threadsafe(self.process_job(batch), loop)
            task.result()
            print("[x] Done processing batch")

        try:
            self._channel.basic_consume(
                queue=BATCH_QUEUE, on_message_callback=callback, auto_ack=True
            )
            print("Worker started")
            # Block on the channel
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self.close()
            print("Worker stopped")

    # TODO: Write a doc explaining error messages and what checking is/isn't supported
    def _check_model_response(self, predictions, labels):
        """
        PRE: response is received from a deserialised pydantic model and labels and types
        have been enforced according to ModelOutput.
        ASSUME: Labels are always correct / have already been validated previously

        Helper function to check the response from the model API and ensure validity compared to data

        Checks are ordered in terms of complexity and computational cost, with the most
        computationally expensive towards the end.

        Params:
        - response : Response object from the model API
        """
        if len(predictions) != len(labels):
            raise WorkerException(
                "Number of model outputs does not match expected number of labels",
                status_code=400,
            )

        if len(labels) >= 0:
            if len(predictions[0]) != len(labels[0]):
                raise WorkerException(
                    "Number of attributes predicted by model does not match number of target attributes",
                    status_code=400,
                )

            for col_index in range(len(labels[0])):
                if not isinstance(
                    predictions[0][col_index], type(labels[0][col_index])
                ):
                    raise WorkerException(
                        "Model output type does not match target attribute type",
                        status_code=400,
                    )
        """
        TODO: Evaluate if this check is necessary -> O(n) complexity where n is number
        of datapoints.
        (As opposed to O(1) complexity or O(d) complexity for above checks)
        """
        num_attributes = len(labels[0])
        for row in predictions[1:]:
            if len(row) != num_attributes:
                raise WorkerException(
                    "Inconsistent number of attributes for each datapoint predicted by model",
                    status_code=400,
                )

        """
        TODO: Evaluate if this check is necessary -> O(n*d) complexity where n is number
        of datapoints in batch and d is number of attributes being predicted.
        (As opposed to O(1) complexity or O(d) complexity for above checks)
        """
        for col_index in range(len(predictions[0])):
            col_type = type(labels[0][col_index])
            for row_index in range(len(predictions)):
                if not isinstance(predictions[row_index][col_index], col_type):
                    raise WorkerException(
                        "All columns for an output label should be of the same type",
                        status_code=400,
                    )

        return

    def convert_to_numeric_classes(self, predicted_labels, true_labels):
        """
        Function to convert labels to numeric classes
        """
        # flatten the labels
        predicted_labels = [label for sublist in predicted_labels for label in sublist]
        true_labels = [label for sublist in true_labels for label in sublist]
        label_set = set(predicted_labels + true_labels)
        print(f"Label set is: {label_set}")
        label_map = {label: i for i, label in enumerate(label_set)}
        predicted_labels_new = [[label_map[label]] for label in predicted_labels]
        true_labels_new = [[label_map[label]] for label in true_labels]
        return predicted_labels_new, true_labels_new

    def binarize_finbert_output(self, predicted_labels, true_labels):
        """
        Function to binarize the output of FinBERT
        """
        # flatten the labels
        predicted_labels = [label for sublist in predicted_labels for label in sublist]
        true_labels = [label for sublist in true_labels for label in sublist]
        # binarize the labels
        predicted_labels = [
            [1] if label == "positive" else [0] for label in predicted_labels
        ]
        true_labels = [[1] if label == "positive" else [0] for label in true_labels]
        return predicted_labels, true_labels


if __name__ == "__main__":
    worker = Worker(host=RABBIT_MQ_HOST)
    worker.run()
