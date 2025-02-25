from pydantic import BaseModel
from abc import ABC
from enum import Enum
from typing import Any


class AggregatorMessage(BaseModel, ABC):
    messageType: str
    message: str
    statusCode: int
    content: Any

    class Config:
        arbitrary_types_allowed = True


class MessageType(str, Enum):
    LOG = "LOG"
    ERROR = "ERROR"
    METRICS_INTERMEDIATE = "METRICS_INTERMEDIATE"
    METRICS_COMPLETE = "METRICS_COMPLETE"
    REPORT = "REPORT"
