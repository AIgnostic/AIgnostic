from metrics.models import (
    CalculateRequest,
    MetricsInfo,
    MetricValues,
)
from metrics.metrics import calculate_metrics as _calculate_metrics
from fastapi import FastAPI

"""
    Contains the API endpoints for the metrics service
"""

metrics_app = FastAPI()

task_to_metric_map = {
    "binary_classification": [
        "disparate_impact",
        "equal_opportunity_difference",
        "equalized_odd_difference",
        "false_negative_rate_difference",
        "negative_predictive_value",
        "positive_predictive_value",
        "statistical_parity_difference",
        "true_positive_rate_difference",
    ],
    "multi_class_classification": [],
    "regression": [],
    "next_token_generation": [],
}
"""Documentation for the metrics service on the API to tell us what metric are supported"""


@metrics_app.get("/retrieve-metric-info", response_model=MetricsInfo)
async def retrieve_info() -> MetricsInfo:
    """
    Retrieve information about the types of tasks expected / supported by the library
    as well as all the metrics that can be calculated for each task type.
    :return: MetricsInfo - contains the mapping from task type to metrics
    """
    return MetricsInfo(task_to_metric_map=task_to_metric_map)


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