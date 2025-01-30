from pydantic import BaseModel

class MetricsInfo(BaseModel):
    """
    Format to receive information about types of metrics available
    """
    tasks_to_metric_map: dict[str, list]


class MetricRequest(BaseModel):
    """
    Format to send metrics info request
    """
    task_type: str


class MetricValues(BaseModel):
    """
    Receive calculated metric values
    """
    metric_values: dict[str, float]