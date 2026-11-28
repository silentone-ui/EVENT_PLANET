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
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        return getattr(request.user, 'role', None) == 'organizer'

class IsEventOwnerOrReadOnly(permissions.BasePermission):
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
        event = getattr(obj, 'event', None)
        if event is None and hasattr(obj, 'stage'):
            event = obj.stage.event
        if event is None and hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        return event is not None and event.organizer == request.user
        