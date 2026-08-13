from rest_framework import permissions

from authentication.models import UserType


class IsActiveAccountPermission(permissions.BasePermission):
    """Chặn tài khoản bị khóa kể cả khi JWT cũ vẫn còn hạn."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and getattr(user, 'status', False)
        )


class IsOrganizerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and getattr(request.user, 'status', False)
            and getattr(request.user, 'type', None) == UserType.ORGANIZER
        )


class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and getattr(request.user, 'status', False)
            and getattr(request.user, 'type', None) == UserType.CUSTOMER
        )


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and getattr(user, 'status', False)
            and (
                getattr(user, 'type', None) == UserType.ADMIN
                or user.is_staff
                or user.is_superuser
            )
        )
