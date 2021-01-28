from datetime import datetime

FAKE_ORGS = {
    'AAAIMX': {
        'name': 'AAAIMX',
        'phone': '9999999',
        'address': 'MID, MX'
    },
    'LHT': {
        'name': 'Lighthouse Tech',
        'phone': '111111',
        'address': 'MID, MX'
    }
}

FAKE_USERS = {
    'ADMIN': {
        'email': 'admin@test.org',
        'name': 'Raul Novelo',
        'password': '12345',
        'phone': '123456789',
        'birthdate': datetime.now()
    },
    'VIEWER': {
        'email': 'viewer@test.org',
        'name': 'Viewer User Example',
        'password': '12345',
        'phone': '987654321',
        'birthdate': datetime.now()
    },
    'USER': {
        'email': 'guest@test.org',
        'name': 'John Doe',
        'password': '12345',
        'phone': '1357908642',
        'birthdate': datetime.now()
    }
}

USER_MODEL_FIELDS = ['id', 'organization', 'groups', 'password', 'last_login', 'is_superuser',
                     'email', 'name', 'birthdate', 'phone', 'date_joined', 'is_staff', 'is_active', 'user_permissions']

USER_INFO_FIELDS = ['id', 'organization', 'email', 'name', 'birthdate', 'phone']

UNAUTHORIZED_MESSAGE = {
    'detail': 'Authentication credentials were not provided.'
}
