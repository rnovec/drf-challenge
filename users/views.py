from django.contrib.auth.models import Group
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserInfoSerializer, GroupSerializer


def isAdmin(user):
    return user.is_staff or user.is_superuser or user.groups.filter(name__in=['Administrator'])


# Create your views here.


class GroupList(generics.ListAPIView):
    """
    A generic List API for viewing group instances.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    filterset_fields = ['phone']
    search_fields = ['name', 'email']
    ordering_fields = []
    ordering = []

    def list(self, request):

        if request.user.groups.filter(name__in=['Administrator', 'Viewer']):
            organization = request.user.organization
            queryset = self.get_queryset().filter(organization=organization)
            queryset = self.filter_queryset(queryset)
        else:
            queryset = User.objects.none()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = UserInfoSerializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
