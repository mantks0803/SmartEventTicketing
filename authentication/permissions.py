from rest_framework import permissions

from authentication.models import UserType


class IsOrganizerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'type', None) == UserType.ORGANIZER
        )


class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'type', None) == UserType.CUSTOMER
        )


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and (
                getattr(user, 'type', None) == UserType.ADMIN
                or user.is_staff
                or user.is_superuser
            )
        )
