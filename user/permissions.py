from rest_framework.permissions import SAFE_METHODS, BasePermission

METHODS = ("GET", "POST", "HEAD", "OPTIONS")


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsAdminOrIfAuthenticatedReadAndCreateOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            (
                request.method in METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
