
import datetime

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Simple JWT
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(hours=1),
    "USER_ID_FIELD": "id",
    'USER_ID_CLAIM': 'user_id',
    'UPDATE_LAST_LOGIN': True
}

# Django Cors Headers
# https://pypi.org/project/django-cors-headers/
# CORS_ORIGIN_WHITELIST = os.environ.get("DJANGO_ALLOWED_ORIGINS").split(' ')

CORS_ALLOW_ORIGINS_ALL = True
CORS_ALLOW_CREDENTIALS = True