"""Custom application exceptions."""


class AppException(Exception):
    """Base application exception with status code and error code."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "INTERNAL_ERROR",
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)
