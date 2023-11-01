from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


METHODS = ("GET", "POST", "HEAD", "OPTIONS")


class IsAdminOrIfAuthenticatedReadAndCreateOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )