from pydantic import BaseModel, field_validator
from typing import Optional, Any
from aignostic.pydantic_models.utils import nested_list_to_np


class MetricsInfo(BaseModel):
    """
    Format to receive information about types of metrics available
    """
    tasks_to_metric_map: dict[str, list]


class CalculateRequest(BaseModel):
    """
    CalculateRequest pydantic model represents the request body when sending a request
    to calculate metrics. It includes list of metrics to be calculated as well as all relevant
    data for the task

    :param metrics: list[str] - list of metrics to be calculated
    :param true_labels: Optional[list[list]] - 2D list of true labels where each nested list
        corresponds to one row of data.
    :param predicted_labels: Optional[list[list]] - 2D list of predicted labels where each
        nested list corresponds to one row of data.
    """
    metrics: list[str]
    true_labels: Optional[list[list]] = None
    predicted_labels: Optional[list[list]] = None
    target_class: Optional[Any] = None

    # Convert the 'true_labels' and 'predicted_labels' into np.arrays
    @field_validator('true_labels', 'predicted_labels', mode='after')
    def convert_true_to_np_arrays(cls, v):
        return nested_list_to_np(v)


class MetricValues(BaseModel):
    """
    Receive calculated metric values
    """
    metric_values: dict[str, float]
