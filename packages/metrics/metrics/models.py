from pydantic import BaseModel, field_validator, HttpUrl, Field
from typing import Optional, Any, Union, Tuple
from common.utils import nested_list_to_np
from metrics.exceptions import _MetricsPackageException
import numpy as np


class MetricsInfo(BaseModel):
    """
    Format to receive information about types of metrics available
    """
    task_to_metric_map: dict[str, list]


class CalculateRequest(BaseModel):
    """
    CalculateRequest pydantic model represents the request body when sending a request
    to calculate metrics. It includes a list of metrics to be calculated as well as all relevant
    data for the task.

    :param metrics: list[str] - List of metrics to be calculated.
    :param task_name: Optional[str] - Name of the task for which metrics are calculated. Options:
        "binary_classification", "multi_class_classification", "regression".
    :param input_data: Optional[list[list]] - 2D list of input data where each nested list
        corresponds to one row of data.
    :param confidence_scores: Optional[list[list]] - 2D list of probabilities where each nested
        list corresponds to one row of data - indicates the probability of a given output prediction
        and all other possible outputs
    :param true_labels: Optional[list[list]] - 2D list of true labels where each nested list
        corresponds to one row of data.
    :param predicted_labels: Optional[list[list]] - 2D list of predicted labels where each
        nested list corresponds to one row of data.
    :param target_class: Optional[Any] - The target class for which metrics are calculated.
    :param privileged_groups: Optional[list[dict[str, Any]]] - List of dictionaries representing
        privileged groups.
    :param unprivileged_groups: Optional[list[dict[str, Any]]] - List of dictionaries representing
        unprivileged groups.
    :param protected_attr: Optional[list[int]] - List of indices representing protected attributes.
    :param model_url: Optional[HttpUrl] - URL of the model endpoint.
    :param model_api_key: Optional[str] - API key for accessing the model endpoint.
    """
    metrics: list[str]
    task_name: Optional[str] = None
    batch_size: Optional[int] = None
    total_sample_size: Optional[int] = None
    input_features: Optional[list[list]] = None
    confidence_scores: Optional[list[list]] = None
    true_labels: Optional[list[list]] = None
    predicted_labels: Optional[list[list]] = None
    target_class: Optional[Any] = None
    privileged_groups: Optional[list[dict[str, Any]]] = None
    unprivileged_groups: Optional[list[dict[str, Any]]] = None
    protected_attr: Optional[list[int]] = None
    model_url: Optional[HttpUrl] = None
    model_api_key: Optional[str] = None

    # TODO: Refactor this to a better implementation
    regression_flag: bool = False

    # Convert the 'true_labels' and 'predicted_labels' into np.arrays
    @field_validator(
        'input_features',
        'confidence_scores',
        'true_labels',
        'predicted_labels',
        'protected_attr',
        mode='after'
    )
    def convert_to_np_arrays(cls, v):
        return nested_list_to_np(v)
    

def convert_calculate_request_to_dict(info: CalculateRequest) -> dict:
    """
    Converts a CalculateRequest object to a JSON-serializable dictionary.

    :param info: CalculateRequest - The internal model representing the metric calculation request.
    :return: dict - A dictionary containing relevant fields, with NumPy arrays converted to lists.
    """
    def safe_convert(value):
        """Recursively convert NumPy arrays to lists for JSON serialization."""
        if isinstance(value, np.ndarray):
            return value.tolist()  # Convert NumPy arrays to lists
        elif isinstance(value, list):  # Ensure nested lists are handled
            return [safe_convert(item) for item in value]
        elif isinstance(value, dict):  # Ensure nested dictionaries are handled
            return {key: safe_convert(val) for key, val in value.items()}
        return value  # Return as is for other types

    return {
        "metrics": info.metrics,
        "task_name": info.task_name,
        "input_data": safe_convert(info.input_features),
        "confidence_scores": safe_convert(info.confidence_scores),
        "true_labels": safe_convert(info.true_labels),
        "predicted_labels": safe_convert(info.predicted_labels),
        "target_class": info.target_class,
        "privileged_groups": safe_convert(info.privileged_groups),
        "unprivileged_groups": safe_convert(info.unprivileged_groups),
        "protected_attr": safe_convert(info.protected_attr),
        "model_url": str(info.model_url) if info.model_url else None,
        "model_api_key": info.model_api_key,
        "batch_size": info.batch_size,
        "total_sample_size": info.total_sample_size,
        "regression_flag": info.regression_flag
    }



class MetricsPackageExceptionModel(BaseModel):
    """
    MetricsPackageExceptionModel is the pydantic model representing fields of the base exception
    class for the metrics package.
    """
    detail: str
    status_code: int
    exception_type: str = Field(default="")

    class Config:
        arbitrary_types_allowed = True


class MetricValue(BaseModel):
    """
    Represents a metric's computed and ideal values, and its min-max range

    :param true_value: float - The true value of the metric
    :param ideal_value: float - The ideal value of the metric
    :param range: Tuple[Optional[float], Optional[float]] - The acceptable range the metric can lie in
    """
    computed_value: float
    ideal_value: float
    range: Tuple[Optional[float], Optional[float]] = (None, None)


class MetricConfig(BaseModel):
    """Receive calculated metric values and other relevant information"""
    metric_values: dict[str, Union[MetricsPackageExceptionModel, MetricValue]]

    @field_validator('metric_values', mode='before')
    def convert_exception_to_model(cls, v):
        if isinstance(v, dict):
            for key, value in v.items():
                if isinstance(value, _MetricsPackageException):
                    v[key] = value.to_pydantic_model()
        return v

    batch_size: int
    total_sample_size: int
    warning_msg: Optional[str] = None


class WorkerResults(MetricConfig):
    """
    Inherit from MetricConfig
    """
    user_id: str
    user_defined_metrics: Optional[dict[str, MetricValue]] = None
