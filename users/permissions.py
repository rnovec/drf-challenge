from rest_framework.permissions import SAFE_METHODS, BasePermission


class OrgPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        has_perms = False
        is_his_org = user.organization.id == obj.id
        if request.method in SAFE_METHODS:
            has_perms = user.groups.filter(
                name__in=['Administrator', 'Viewer'])
        if request.method == 'PATCH':
            has_perms = user.groups.filter(name__in=['Administrator'])
        return has_perms and is_his_org


class UserPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_owner = request.user.id == obj.id
        is_admin = user.groups.filter(name__in=['Administrator'])
        if request.method in SAFE_METHODS:
            is_admin_or_viewer = user.groups.filter(
                name__in=['Administrator', 'Viewer'])
            return is_admin_or_viewer or is_owner
        if request.method == 'PATCH':
            return is_admin or is_owner
        if request.method == 'DELETE':
            return is_admin


class UserOrgPermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        is_his_org = user.organization.id == self.kwargs['org_id']
        if request.method == 'GET':
            has_perms = user.groups.filter(
                name__in=['Administrator', 'Viewer'])
        return has_perms and is_his_org