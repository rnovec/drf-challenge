# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
)

THIRD_PARTY_APPS = (
    'drf_yasg',
    'corsheaders',
    'rest_framework',
    'django_filters',
)

LOCAL_APPS = (
    'users',
)

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS
