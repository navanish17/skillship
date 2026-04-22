"""
TenantMiddleware — injects request.school_id on every request.

Must run AFTER AuthenticationMiddleware so request.user is available.
Views and managers use request.school_id to scope all queries.
"""


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Default: no tenant scope (anonymous users, MAIN_ADMIN)
        request.school_id = None

        if hasattr(request, "user") and request.user.is_authenticated:
            # MAIN_ADMIN has school=NULL — they operate across all schools
            request.school_id = request.user.school_id

        return self.get_response(request)
