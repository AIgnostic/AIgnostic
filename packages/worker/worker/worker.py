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
from common.models.common import Job
from common.rabbitmq.connect import connect_to_rabbitmq, init_queues
import requests
from pydantic.networks import HttpUrl
import metrics.metrics as metrics_lib
import json
from typing import Optional
import asyncio
from common.models import CalculateRequest, MetricConfig
import random

from common.rabbitmq.constants import JOB_QUEUE, RESULT_QUEUE

from pika.adapters.blocking_connection import BlockingChannel


connection = None
channel: BlockingChannel = None
RABBIT_MQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")


class WorkerException(Exception):
    def __init__(self, detail: str, status_code: int = 500):
        """Custom exception class for workers

        Args:
            detail (str): Description of error that occured
            status_code (int, optional): HTTP status code to report back to the client. Defaults to 500.
        """
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class Worker():
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
        init_queues(self._channel)
        print("Connection established to RabbitMQ")

    def queue_result(self, result: MetricConfig):
        """
        Function to queue the results of a job
        """
        self._channel.basic_publish(
            exchange="", routing_key=RESULT_QUEUE, body=result.model_dump_json()
        )
        print("Result: ", result)

    def queue_error(self, error: str):
        """
        Function to queue an error message
        """
        self._channel.basic_publish(
            exchange="", routing_key=RESULT_QUEUE, body=json.dumps({"error": error})
        )

    def close(self):
        self._channel.close()

    def fetch_job(self) -> Optional[Job]:
        """
        Function to fetch a job from the job queue
        """
        method_frame, header_frame, body = self._channel.basic_get(queue=JOB_QUEUE, auto_ack=True)
        if method_frame:
            job_data = json.loads(body)
            print(f"Received job: {job_data}")
            try:
                print("Unpacking job data")
                return Job(**job_data)
            except ValueError as e:
                raise WorkerException(f"Invalid job format: {e}", status_code=400)
        return None

    async def fetch_data(self, data_url: HttpUrl, dataset_api_key, batch_size: int) -> dict:
        """
        Helper function to fetch data from the dataset API

        Params:
        - dataURL : API URL of the dataset
        """
        # Send a GET request to the dataset API
        if dataset_api_key is None:
            response = requests.get(data_url, params={"n": batch_size})
        else:
            response = requests.get(
                data_url,
                headers={"Authorization": f"Bearer {dataset_api_key}"},
                params={"n": batch_size}
            )

        try:
            # Raise errpr if the request was not successful
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WorkerException(
                response.json()["detail"], status_code=response.status_code
            )

        try:
            # Parse the response JSON
            data = response.json()

            # Return the data
            return data
        except Exception as e:
            raise WorkerException(f"Error while fetching data: {e}")

    async def query_model(self, model_url: HttpUrl, data: dict, model_api_key):
        """
        Helper function to query the model API

        Params:
        - modelURL : API URL of the model
        - data : Data to be passed to the model in JSON format with DataSet pydantic model type
        - modelAPIKey : API key for the model
        """
        # Send a POST request to the model API
        if model_api_key is None:
            response = requests.post(url=model_url, json=data)
        else:
            response = requests.post(
                url=model_url,
                json=data,
                headers={"Authorization": f"Bearer {model_api_key}"},
            )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise WorkerException(
                detail=e.response.json()["detail"], status_code=e.response.status_code
            )

        self._check_model_response(response, data["labels"])

        try:
            # Check if the request was successful

            # Parse the response JSON
            data = response.json()

            # Return the data
            return data
        except Exception as e:
            raise WorkerException(
                f"Could not parse model response - {e}; response = {response.text}"
            )

    async def process_job(self, job: Job):

        # fetch data from datasetURL
        data: dict = await self.fetch_data(job.data_url, job.data_api_key, job.batch_size)

        # strip the label from the datapoint
        try:
            features = data["features"]
            labels = data["labels"]
            group_ids = data["group_ids"]
        except KeyError:
            raise WorkerException("KeyError occurred during data processing")
        except Exception:
            raise WorkerException("Error while processing data")

        # TODO: Separate model input and dataset output so labels and group IDs are not passed to the model

        # TODO: Refactor to use pydantic models
        predictions = await self.query_model(
            job.model_url,
            {"features": features, "labels": labels, "group_ids": group_ids},
            job.model_api_key,
        )

        try:
            predicted_labels = predictions["predictions"]

            print(f"Predicted labels: {predicted_labels}")
            print(f"True labels: {labels}")
            print(f"Metrics to compute: {job.metrics}")

            # some preprocessing for FinBERT
            # TODO: Need to sort out how to handle this properly
            if job.model_type == "binary classification":
                predicted_labels, true_labels = self.binarize_finbert_output(predicted_labels, labels)
            elif job.model_type == "multi class classification":
                predicted_labels, true_labels = self.convert_to_numeric_classes(predicted_labels, labels)

            print(f"Predicted labels: {predicted_labels}")
            print(f"True labels: {true_labels}")
            print(f"Confidence scores: {predictions['confidence_scores']}")

            # Construct CalculateRequest
            metrics_request = CalculateRequest(
                metrics=job.metrics,
                batch_size=job.batch_size,
                input_features=features,
                total_sample_size=job.total_sample_size,
                true_labels=true_labels,
                predicted_labels=predicted_labels,
                confidence_scores=predictions["confidence_scores"],
                # TODO: Do this group stuff properly
                privileged_groups=[{"protected_attr": 1}],
                unprivileged_groups=[{"protected_attr": 0}],
                protected_attr=[random.randint(0, 1) for _ in range(len(true_labels))],
                model_url=job.model_url,
                model_api_key=job.model_api_key,
            )
            metrics_results = metrics_lib.calculate_metrics(metrics_request)
            print(f"Final Results: {metrics_results}")
            self.queue_result(metrics_results)
            return
        except Exception as e:
            raise WorkerException(f"Error while processing data: {e}")

    def run(self):
        self.connect()
        try:
            while True:
                job = self.fetch_job()
                if job:
                    asyncio.run(self.process_job(job))
        except KeyboardInterrupt:
            self.close()
            print("Worker stopped")

    # TODO: Write a doc explaining error messages and what checking is/isn't supported
    def _check_model_response(self, response, labels):
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
        predictions = response.json()["predictions"]
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
                if not isinstance(predictions[0][col_index], type(labels[0][col_index])):
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
        predicted_labels = [[1] if label == "positive" else [0] for label in predicted_labels]
        true_labels = [[1] if label == "positive" else [0] for label in true_labels]
        return predicted_labels, true_labels


if __name__ == "__main__":
    worker = Worker(host=RABBIT_MQ_HOST)
    worker.run()
