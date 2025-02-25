from metrics.models import (
    CalculateRequest,
    MetricsInfo,
    MetricConfig,
)
from metrics.metrics import (
    MetricsException,
    task_type_to_metric,
    calculate_metrics as _calculate_metrics
)
from fastapi import FastAPI, HTTPException

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


@metrics_app.post("/calculate-metrics", response_model=MetricConfig)
async def calculate_metrics(info: CalculateRequest) -> MetricConfig:
    """
    calculate_metrics, given a request for calculation of certain metrics and information
    necessary for calculation, attempt to calculate and return the metrics and their scores
    for the given model and dataset.

    :param info: CalculateRequest - contains list of metrics to be calculated and additional
    data required for calculation of these metrics.
    :return: MetricConfig - contains the calculated metrics and their scores
    """
    try:
        return _calculate_metrics(info)
    except MetricsException as e:
        raise HTTPException(status_code=500, detail=e.detail)
