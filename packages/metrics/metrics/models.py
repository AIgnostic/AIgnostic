from pydantic import BaseModel, field_validator, HttpUrl, Field
from typing import Optional, Any, Union, Tuple
from common.utils import nested_list_to_np
from metrics.exceptions import _MetricsPackageException


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
