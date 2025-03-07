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
from common.models.pipeline import Batch, JobStatus, JobStatusMessage
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues, publish_to_queue
from metrics.models import WorkerResults, convert_calculate_request_to_dict
import requests
from pydantic.networks import HttpUrl
import metrics.metrics as metrics_lib
from typing import Optional
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

    def queue_result(self, result: WorkerResults):
        """
        Function to queue the results of a job
        """
        job = AggregatorJob(job_type=JobType.RESULT, content=result)

        self._channel = publish_to_queue(
            self._channel, RESULT_QUEUE, job.model_dump_json()
        )

    def queue_error(self, error: WorkerError):
        """
        Function to queue an error message
        """
        job = AggregatorJob(
            job_type=JobType.ERROR,
            content=error,
        )
        self._channel = publish_to_queue(
            self._channel, RESULT_QUEUE, job.model_dump_json()
        )

    def close(self):
        self._channel.close()

    def fetch_batch(self) -> Optional[Batch]:
        """
        Function to fetch a batch from the job queue
        """
        method_frame, header_frame, body = self._channel.basic_get(
            queue=BATCH_QUEUE, auto_ack=True
        )
        if method_frame:
            batch_data = json.loads(body)
            print(f"Received job: {batch_data}")
            try:
                print("Unpacking batch data")
                return Batch(**batch_data)
            except ValueError as e:
                raise WorkerException(f"Invalid batch format: {e}", status_code=400)
        return None

    async def fetch_data(
        self, data_url: HttpUrl, dataset_api_key, batch_size: int
    ) -> DatasetResponse:
        """
        Helper function to fetch data from the dataset API

        Params:
        - dataURL : API URL of the dataset
        """
        # Send a GET request to the dataset API
        if dataset_api_key is None:
            response = requests.get(
                convert_localhost_url(str(data_url)), params={"n": batch_size}
            )
        else:
            response = requests.get(
                convert_localhost_url(str(data_url)),
                headers={"Authorization": f"Bearer {dataset_api_key}"},
                params={"n": batch_size},
            )

        try:
            response.raise_for_status()
        except Exception as e:
            if e.response and e.response.json():
                raise WorkerException(
                    detail=e.response.json()["detail"],
                    status_code=e.response.status_code,
                )
            else:
                raise WorkerException(
                    detail=f"An unknown exception occured: {e}", status_code=400
                )

        try:
            # Parse the response JSON
            dataset_response = DatasetResponse(**response.json())
            # Return the data
            return dataset_response
        except ValidationError as e:
            raise WorkerException(
                f"Data error - data returned from data provider of incorrect format: \n{e}"
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

        # Send a POST request to the model API
        if model_api_key is None:
            response = requests.post(
                url=convert_localhost_url(str(model_url)), json=data.model_dump_json()
            )
        else:
            response = requests.post(
                url=convert_localhost_url(str(model_url)),
                json=data.model_dump(),
                headers={"Authorization": f"Bearer {model_api_key}"},
            )

        try:
            response.raise_for_status()
        except Exception as e:
            if e.response and e.response.json():
                raise WorkerException(
                    detail=e.response.json()["detail"],
                    status_code=e.response.status_code,
                )
            else:
                raise WorkerException(
                    detail=f"An unknown exception occured: {e}", status_code=400
                )

        try:
            # Check if the request was successful

            # Parse the response JSON
            model_response = ModelResponse(**response.json())
            self._check_model_response(model_response.predictions, data.labels)

            # Return the model response
            return model_response
        except Exception as e:
            raise WorkerException(
                f"Could not parse model response - {e}; response = {response.text}"
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
            try:
                # query the user metric server to get the user-defined metrics
                user_metrics_server_response = requests.get(
                    f"{USER_METRIC_SERVER_URL}/inspect-uploaded-functions/{worker_results.user_id}",
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
                            "user_id": worker_results.user_id,
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

            print(f"Final Results: {worker_results}")
            self.queue_result(worker_results)
            self.send_status_completed(batch.job_id, batch.batch_id)
            return
        except WorkerException as e:
            # known/caught error
            # should be sent back to user
            self.queue_error(
                WorkerError(error_message=e.detail, error_code=e.status_code)
            )
            self.send_status_error(batch.job_id, batch.batch_id, e)
        except Exception as e:
            self.queue_error(
                WorkerError(error_message="An unknown error occurred", error_code=500)
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
        try:
            while True:
                job = self.fetch_batch()
                if job:
                    asyncio.run(self.process_job(job))
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
