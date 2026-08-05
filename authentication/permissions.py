from rest_framework import permissions

class IsOrganizerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'type', None) == 'ORGANIZER'
        )

class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'type', None) == 'CUSTOMER'
        )