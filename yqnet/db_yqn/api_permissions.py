# Copyright: Michael Wood 2019
# Web: http://michaelwood.me.uk
# License: LICENSE.txt

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to do anything
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return obj.user == request.user

class IsInOwners(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to do anything
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return request.user in obj.users.all()

