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
    A generic List API for viewing group instances.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class InfoAPIView(views.APIView):
    """
    An API for viewing user and server info.
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
            'public_ip': request.get_host()
        })


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    A viewset for viewing and editing org instances.
    """
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    permission_classes = (OrgPermissions,)
    http_method_names = ['get', 'patch', 'options', 'head']
    ordering_fields = []
    ordering = []


class UserOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing users org instances.
    """
    serializer_class = UserOrgSerializer
    queryset = User.objects.all()
    ordering_fields = []
    ordering = []

    def get_queryset(self):
        pk = self.kwargs.get('org_id')
        try:
            org = Organization.objects.get(pk=pk)
            return User.objects.filter(organization=org)
        except Organization.DoesNotExist:
            return User.objects.none()

    def list(self, request, *args, **kwargs):
        """
        List all the users for the user organization if user is `Administrator` or `Viewer`.
        """
        org_id = kwargs['org_id']
        org = Organization.objects.get(pk=org_id)

        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        is_his_org = request.user.organization == org

        if not (is_admin_or_viewer and is_his_org):
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve user **id** and **name** if user is `Administrator` or `Viewer`
        """
        instance = self.get_object()

        org_id = kwargs['org_id']
        org = Organization.objects.get(pk=org_id)

        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        is_his_org = request.user.organization == org

        if not (is_admin_or_viewer and is_his_org):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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

    def list(self, request):
        """
        List all the users for the user organization if user is `Administrator` or `Viewer`.
        """
        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        if not is_admin_or_viewer:
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create an user for the organization, must set password as well.
        Request user must be `Administrator`
        """
        is_admin = request.user.groups.filter(name__in=['Administrator'])
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(org=request.user.organization)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
