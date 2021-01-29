"""
Constant used in tests and serializers definition
"""

USER_MODEL_FIELDS = (
    'id', 'organization', 'groups', 'password', 'last_login', 'is_superuser',
    'email', 'name', 'birthdate', 'phone', 'date_joined', 'is_staff',
    'is_active', 'user_permissions'
)

USER_INFO_FIELDS = (
    'id', 'organization',
    'email', 'name', 'birthdate', 'phone'
)

USER_CREATE_FIELDS = (
    'id', 'name', 'phone', 'email',
    'birthdate', 'groups', 'password'
)

ORG_INFO_FIELDS = (
    'id', 'name', 'phone', 'address'
)

UNAUTHORIZED_MESSAGE = {
    'detail': 'Authentication credentials were not provided.'
}

ADMIN = 'Administrator'
VIEWER = 'Viewer'