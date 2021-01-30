"""
Application have:
- Administrator: Full access to CRUD Any User in his org and RU Organization
- Viewer: List and Retrieve and User in his org.
- User: CRU his own user
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission
from .constants import ADMIN, VIEWER


def is_admin(user):
    return bool(user.groups.filter(name__in=[ADMIN]))


def is_viewer(user):
    return bool(user.groups.filter(name__in=[VIEWER]))


def is_admin_or_viewer(user):
    return bool(user.groups.filter(name__in=[ADMIN, VIEWER]))


class OrgPermissions(BasePermission):
    """
    Permission for Organization Endpoints:

    - GET /api/organizations/{id}/ Retrieve organization information 
    if request user is `Administrator` or `Viewer`.

    - PATCH /api/organizations /{id} Update organization if request user is `Administrator`.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_his_org = user.organization.id == obj.id

        if request.method in SAFE_METHODS:
            return is_admin_or_viewer(user)

        if request.method == 'PATCH':
            return is_admin(user) and is_his_org


class UserPermissions(BasePermission):
    """
    Permission for User Endpoints:

    - GET /api/users/ List all the users for the user organization 
    if user is `Administrator` or `Viewer`.

    - GET /api/users/{id}/ Retrieve user information, and the organization id and name

    - POST /api/users/ Request user must be Administrator

    - PATCH /api/users/{id} Update user information for the user_id 
    if request user is `Administrator` of his organization. Or request user is user_id

    - DELETE /api/users/{id} Delete user for the user_id 
    if request user is `Administrator` of his organization
    """

    def has_permission(self, request, view):
        user = request.user
        user_id = view.kwargs.get('pk', None)

        if request.method == 'POST':
            return is_admin(user)

        if request.method == 'GET' and not user_id:
            return is_admin_or_viewer(user)

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_owner = user.id == obj.id

        if request.method in SAFE_METHODS:
            return is_admin_or_viewer(user) or is_owner

        if request.method == 'PATCH':
            return is_admin(user) or is_owner

        if request.method == 'DELETE':
            return is_admin(user)


class UserOrgPermissions(BasePermission):
    """
    Permission for Organization User Endpoints:

    - GET /api/organization/{id}/users List all the users for the user organization 
    if user is `Administrator` or `Viewer`.

    - GET /api/organization/{id}/users/{id}/ Retrieve user id and name 
    if user is `Administrator` or `Viewer`
    """

    def has_permission(self, request, view):
        user = request.user
        org_id = int(view.kwargs['org_id'])
        is_his_org = user.organization.id == org_id

        if request.method == 'GET':
            return is_admin_or_viewer(user) and is_his_org
