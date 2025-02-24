from pydantic import BaseModel, field_validator, HttpUrl
from typing import Optional, Any
from common.utils import nested_list_to_np


class MetricsInfo(BaseModel):
    """
    Format to receive information about types of metrics available
    """
    tasks_to_metric_map: dict[str, list]


class CalculateRequest(BaseModel):
    """
    CalculateRequest pydantic model represents the request body when sending a request
    to calculate metrics. It includes a list of metrics to be calculated as well as all relevant
    data for the task.

    :param metrics: list[str] - List of metrics to be calculated.
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


class MetricValues(BaseModel):
    """
    Receive calculated metric values
    """
    metric_values: dict[str, float]
    metric_range: dict[str, ((float, float), float)]
    batch_size: int
    total_sample_size: int
    warning_msg: Optional[str] = None
