# permissions.py

from rest_framework.permissions import BasePermission

class IsSellerUser(BasePermission):
    """
    Allows access only to users with is_seller=True.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_seller)


# permissions.py

from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Allows access only to users with is_admin=True.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)
