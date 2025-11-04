from rest_framework import permissions


class IsArticleOwner(permissions.BasePermission):
    """Custom permission to only allow article owners to edit/delete"""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the article owner
        return obj.author == request.user