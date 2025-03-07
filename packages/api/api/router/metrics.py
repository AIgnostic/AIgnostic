from metrics.models import (
    CalculateRequest,
    MetricsInfo,
    MetricValues,
)
from metrics.metrics import calculate_metrics as _calculate_metrics, task_type_to_metric
from fastapi import FastAPI

"""
    Contains the API endpoints for the metrics service
"""

metrics_app = FastAPI()


@metrics_app.get("/retrieve-metric-info", response_model=MetricsInfo)
async def retrieve_info() -> MetricsInfo:
    """
    Retrieve information about the types of tasks expected / supported by the library
    as well as all the metrics that can be calculated for each task type.
    :return: MetricsInfo - contains the mapping from task type to metrics
    """
    return MetricsInfo(task_to_metric_map=task_type_to_metric)


@metrics_app.post("/calculate-metrics", response_model=MetricValues)
async def calculate_metrics(info: CalculateRequest) -> MetricValues:
    """
    calculate_metrics, given a request for calculation of certain metrics and information
    necessary for calculation, attempt to calculate and return the metrics and their scores
    for the given model and dataset.
    :param info: CalculateRequest - contains list of metrics to be calculated and additional
    data required for calculation of these metrics.
    :return: MetricValues - contains the calculated metrics and their scores
    """
    return _calculate_metrics(info)
