from abc import ABC, abstractmethod
from warnings import warn


class _MetricsPackageException(Exception, ABC):
    """
    _MetricsPackageException is the base exception class for the metrics package
        - it extends Exception as an abstract class and requires a non-empty detail field
        to describe an error as well as a status code.
    """
    @abstractmethod
    def __init__(self, detail, status_code):
        if not detail:
            warn("Exception raised without a detailed message - please provide a message")
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)

    @abstractmethod
    def to_pydantic_model(self) -> dict:
        return {
            "detail": self.detail,
            "status_code": self.status_code,
            "exception_type": self.__class__.__name__
        }


class MetricsComputationException(_MetricsPackageException):
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


class DataInconsistencyException(_MetricsPackageException):
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


class ModelQueryException(_MetricsPackageException):
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


class DataProvisionException(_MetricsPackageException):
    """
    Class representing insufficient data provision for metric calculations - this occurs when
    the user's choice of metrics require certain extra data to be provided. If the conditions
    to calculate a metric are not satisfied, this exception is raised.
    """

    # This is a 400 error as metrics is implemented as a microservice
    def __init__(self, detail=None, status_code=400):
        err_msg = "Insufficient or invalid data provided to calculate user metrics"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)


class InvalidParameterException(_MetricsPackageException):
    """
    Class representing invalid parameter values for metric calculations - this occurs when
    the a function not accepting the provided parameter values.
    """

    # This is a 400 error as metrics is implemented as a microservice
    def __init__(self, detail=None, status_code=400):
        err_msg = "Invalid parameter values provided"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)
