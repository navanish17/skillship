"""
Development settings — DEBUG on, permissive CORS, console email.
Activate via: DJANGO_SETTINGS_MODULE=config.settings.dev
"""

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# ── CORS — allow the Next.js dev server ───────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ── Email — print to console instead of sending ──────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Throttle — disable in dev so we don't hit limits while testing ───────────
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405

# ── DRF Browsable API — useful during development ───────────────────────────
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
