"""
Custom exception types for business-rule violations.

Service layer raises these; the DRF exception handler converts them to
clean JSON responses with a machine-readable `code` field.
"""

from rest_framework.views import exception_handler as drf_exception_handler


class DomainError(Exception):
    """Base class for all business-rule errors."""

    def __init__(self, message: str = "An error occurred", code: str = "error", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Not found", code: str = "not_found"):
        super().__init__(message=message, code=code, status_code=404)


class PermissionDeniedError(DomainError):
    def __init__(self, message: str = "Permission denied", code: str = "permission_denied"):
        super().__init__(message=message, code=code, status_code=403)


class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict", code: str = "conflict"):
        super().__init__(message=message, code=code, status_code=409)


def api_exception_handler(exc, context):
    """
    DRF exception handler that also catches our DomainError family.
    Wired in settings.REST_FRAMEWORK["EXCEPTION_HANDLER"].
    """
    # Let DRF handle its own exceptions first (validation errors, auth errors, etc.)
    response = drf_exception_handler(exc, context)

    if response is not None:
        return response

    # Handle our custom domain errors
    if isinstance(exc, DomainError):
        from rest_framework.response import Response

        return Response(
            {"code": exc.code, "message": exc.message},
            status=exc.status_code,
        )

    # Anything else is unhandled — let Django's 500 handler deal with it
    return None
