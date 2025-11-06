from rest_framework import permissions


class IsProfileOwnerORAdmin(permissions.BasePermission):
    """Custom permission to only allow profile owners or admins to edit/delete"""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request for SAFE_METHODS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the profile owner or admin
        return obj == request.user or request.user.is_staff