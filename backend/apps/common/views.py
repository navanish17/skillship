"""Health check endpoint — returns 200 if the service is alive."""

from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def healthz(request):
    """Lightweight health check for load balancers / uptime monitors."""
    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        pass

    status_code = 200 if db_ok else 503
    return Response(
        {"status": "ok" if db_ok else "degraded", "db": db_ok},
        status=status_code,
    )
