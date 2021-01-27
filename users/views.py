from django.contrib.auth.models import Group
from rest_framework import (
    viewsets,
    generics,
    status,
    permissions,
    mixins
)
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Organization
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


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    A viewset for viewing and editing org instances.
    """
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    http_method_names = ['get', 'patch', 'options', 'head']

    ordering_fields = []
    ordering = []

    def retrieve(self, request, pk=None):
        """
        Retrieve organization information if request user is `Administrator` or `Viewer`
        """
        instance = self.get_object()

        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        is_his_org = request.user.organization.id == instance.id

        if not (is_admin_or_viewer and is_his_org):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        is_admin = request.user.groups.filter(name__in=['Administrator'])
        is_his_org = request.user.organization.id == instance.id

        if not (is_admin and is_his_org):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Update organization if request user is `Administrator`.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class UserOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing users org instances.
    """
    serializer_class = UserOrgSerializer
    queryset = User.objects.all()

    ordering_fields = []
    ordering = []

    def get_queryset(self):
        pk = self.kwargs['org_id']
        org = Organization.objects.get(pk=pk)
        return User.objects.filter(organization=org)

    def list(self, request, *args, **kwargs):
        """
        List all the users for the user organization if user is `Administrator` or `Viewer`.
        """
        pk = kwargs['org_id']
        org = Organization.objects.get(pk=pk)

        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        is_his_org = request.user.organization == org

        if not (is_admin_or_viewer and is_his_org):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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

        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        if not is_admin_or_viewer:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = UserInfoSerializer
    queryset = User.objects.all()
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

    def list(self, request):
        """
        List all the users for the user organization if user is `Administrator` or `Viewer`.
        """
        is_admin_or_viewer = request.user.groups.filter(
            name__in=['Administrator', 'Viewer'])
        if not is_admin_or_viewer:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        org = request.user.organization
        queryset = self.filter_queryset(User.objects.filter(organization=org))

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
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(org=request.user.organization)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk=None):
        """
        Retrieve user information, and the organization id and name
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        is_admin = request.user.groups.filter(name__in=['Administrator'])
        is_his_org = request.user.organization == instance.organization
        is_owner = request.user == instance

        if not (is_admin and is_his_org) and not is_owner:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Update user information for the user_id if request user is `Administrator`
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        Delete user for the **user_id** if request user is `Administrator` of his organization
        """
        instance = self.get_object()

        is_admin = request.user.groups.filter(name__in=['Administrator'])
        is_his_org = request.user.organization == instance.organization
        if not (is_admin and is_his_org):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
