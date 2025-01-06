from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    A permission that allows users to edit or delete only their own posts.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access only to the owner of the object
        if request.method in permissions.SAFE_METHODS:
            return True  # Reading is allowed for everyone
        return obj.user == request.user  # Changes are allowed only to the owner
