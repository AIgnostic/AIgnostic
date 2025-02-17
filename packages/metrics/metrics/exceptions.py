from abc import ABC, abstractmethod


class __MetricsPackageException(Exception, ABC):

    @abstractmethod
    def __init__(self, detail, status_code):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class MetricsException(__MetricsPackageException):

    def __init__(self, metric_name, detail=None, status_code=500):
        err_msg = f"Error during metric calculation ({metric_name})"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)


class ModelQueryException(__MetricsPackageException):

    def __init__(self, detail=None, status_code=400):
        err_msg = "Error when querying model"
        if detail:
            err_msg += f": {detail}"
        super().__init__(err_msg, status_code)
