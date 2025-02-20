from abc import ABC, abstractmethod
from warnings import warn


class __MetricsPackageException(Exception, ABC):
    """
    __MetricsPackageException is the base exception class for the metrics package
        - it extends Exception as an abstract class and requires a detail field (not empty)
        to describe an error as well as a status code.

    """
    @abstractmethod
    def __init__(self, detail, status_code):
        if not detail:
            warn("Exception raised without a detailed message - please provide a message")
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class MetricsException(__MetricsPackageException):
    """
    Class for all metric-related exceptions (as a result of metric calculation).

    Args:
        metric_name: [str] - Name of the metric that caused the error.
        detail: [str | None] = None - Error message to display to the user. Default message is
            "Error during metric calculation ({metric_name})". Having a non-empty detail
            message will append it to the default message with ": {detail}".
        status_code: [int] = 500 - HTTP status code to return to the user.
    """
    def __init__(self, metric_name, detail=None, status_code=500):
        err_msg = f"Error during metric calculation ({metric_name})"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)


class DataInconstencyException(__MetricsPackageException):
    """
    Class representing invalid inputs for metric calculations - specifically regarding
    .e.g. inconsistent number of datapoints or other data inconstency issues

    Args:
        detail: [str | None] = None - Error message to display to the user. Default message is
            "Data inconsistency error". Having a non-empty detail message will append it to the
            default message with ": {detail}".
        status_code: [int] = 400 - HTTP status code to return to the user.
    """

    def __init__(self, detail=None, status_code=400):
        err_msg = "Data inconsistency error"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)

class ModelQueryException(__MetricsPackageException):
    """
    Class for all model query-related exceptions (as a result of querying the model during
    metric calculations or otherwise).

    Args:
        detail: [str | None] = None - Error message to display to the user. Default message is
            "Error when querying model". Having a non-empty detail message will append it to the
            default message with ": {detail}".
        status_code: [int] = 400 - HTTP status code to return to the user.
    """
    def __init__(self, detail=None, status_code=400):
        err_msg = "Error when querying model"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)
