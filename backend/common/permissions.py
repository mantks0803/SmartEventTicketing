from rest_framework import permissions

class IsOrganizerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.type == 'ORGANIZER'
        )

class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.type == 'CUSTOMER'
        )