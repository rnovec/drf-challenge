"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import path
from django.views.generic.base import TemplateView

from rest_framework import routers, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.views import (
    UserViewSet,
    GroupList,
    OrganizationViewSet,
    UserOrganizationViewSet,
    InfoAPIView
)

schema_view = get_schema_view(
    openapi.Info(
        title="DRF Exercise API",
        default_version='v1',
        description="API for Lighthouse DRF Challenge",
        contact=openapi.Contact(email="raul.novelo@aaaimx.org"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'organizations/(?P<org_id>.+)/users',
                UserOrganizationViewSet, basename='organizations')

auth_urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('groups/', GroupList.as_view(), name='list_auth_groups'),
]

apidocs_urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger',
                                           cache_timeout=0), name='schema-swagger-ui')
]

api_urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
    path('info/', InfoAPIView.as_view()),
    path('docs/', include(apidocs_urlpatterns))
]

urlpatterns = [
    path('', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
