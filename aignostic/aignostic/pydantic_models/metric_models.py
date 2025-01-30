from pydantic import BaseModel, validator
from typing import Optional, Any
from aignostic.pydantic_models.utils import nested_list_to_np


class MetricsInfo(BaseModel):
    """
    Format to receive information about types of metrics available
    """
    tasks_to_metric_map: dict[str, list]


class CalculateRequest(BaseModel):
    """
    task_type: Type of task for which metric is calculated
    calculation_info: Data required to calculate metrics .e.g. true vs predicted
    """
    metrics: list[str]
    true_labels: Optional[list[list]] = None
    predicted_labels: Optional[list[list]] = None
    target_class: Optional[Any] = None
    
    # Convert the 'true_labels' and 'predicted_labels' into np.arrays
    @validator('true_labels', pre=False, always=True)
    def convert_to_np_arrays(cls, v):
        return nested_list_to_np(v)
    
        # Convert the 'true_labels' and 'predicted_labels' into np.arrays
    @validator('predicted_labels', pre=False, always=True)
    def convert_to_np_arrays(cls, v):
        return nested_list_to_np(v)


class MetricValues(BaseModel):
    """
    Receive calculated metric values
    """
    metric_values: dict[str, float]