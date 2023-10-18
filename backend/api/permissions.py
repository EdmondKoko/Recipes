from rest_framework import permissions


class IsAuthorOrAdminOnly(permissions.BasePermission):
    """Разрешение, которое позволяет только автору или администратору выполнять действия."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, value):
        return (
            request.method in permissions.SAFE_METHODS
            or value.author == request.user
        )
