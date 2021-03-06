from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework import (
    viewsets,
    generics,
    status,
    mixins,
    views
)
from rest_framework.compat import coreapi
from rest_framework.response import Response

from .models import User, Organization
from .permissions import (
    OrgPermissions,
    UserPermissions,
    UserOrgPermissions
)
from .serializers import (
    GroupSerializer,
    UserDefaultSerializer,
    UserInfoSerializer,
    UserCreateSerializer,
    UserOrgSerializer,
    OrganizationSerializer
)


class GroupList(generics.ListAPIView):
    """
    A generic List API for viewing Authentication Groups.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class InfoAPIView(views.APIView):
    """
    API for viewing user and server info.
    """

    def get(self, request):
        """
        GET user name, organization and server information
        Should return {`user_name`, `id`, `organization_name`, `public_ip`}
        """
        return Response({
            'id': request.user.id,
            'user_name': request.user.name,
            'organization_name': request.user.organization.name,
            'public_ip': request.META.get('REMOTE_ADDR')
        })


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    A viewset for viewing and editing org instances.
    """
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    permission_classes = [OrgPermissions, ]
    http_method_names = ['get', 'patch', 'options', 'head']
    ordering_fields = []
    ordering = []


class UserOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing users org instances.
    """
    serializer_class = UserOrgSerializer
    queryset = User.objects.all()
    permission_classes = (UserOrgPermissions,)
    ordering_fields = []
    ordering = []

    def get_queryset(self):
        pk = self.kwargs.get('org_id')
        try:
            org = Organization.objects.get(pk=pk)
            return User.objects.filter(organization=org)
        except Organization.DoesNotExist:
            return User.objects.none()


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = UserInfoSerializer
    queryset = User.objects.all()
    permission_classes = (UserPermissions,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']

    filterset_fields = ['phone']
    search_fields = ['name', 'email']
    ordering_fields = []
    ordering = []

    def get_serializer_class(self):
        if self.action == 'list':
            return UserDefaultSerializer
        if self.action == 'create':
            return UserCreateSerializer
        return UserInfoSerializer

    def get_queryset(self):
        org = self.request.user.organization
        return User.objects.filter(organization=org)

    def create(self, request):
        """
        Create an user for the organization, must set password as well.
        Request user must be `Administrator`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(org=request.user.organization)  # set the same org

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
