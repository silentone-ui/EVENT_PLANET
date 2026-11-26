from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):


        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user



    from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'organizer'
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user