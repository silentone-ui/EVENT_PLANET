from rest_framework import viewsets, permissions
from .models import Event
from .serializers import EventSerializer
from core.permissions import IsOrganizerOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)