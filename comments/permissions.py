from rest_framework import permissions


class IsCommentOwnerOrArticleOwner(permissions.BasePermission):
    """
    Custom permission to allow:
    - Comment owners to update their comments
    - Comment owners AND article owners to delete comments
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions require authentication
        if not request.user.is_authenticated:
            return False

        # For update operations, only comment owner can update
        if request.method in ['PUT', 'PATCH']:
            return obj.user == request.user

        # For delete operations, both comment owner and article owner can delete
        if request.method == 'DELETE':
            return obj.user == request.user or obj.article.author == request.user

        return False