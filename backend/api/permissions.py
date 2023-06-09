from rest_framework.permissions import BasePermission


class IsAuthorOrAdminOnly(BasePermission):
    def has_object_permission(self, request, view, value):
        return value.author == request.user or request.user.is_superuser
