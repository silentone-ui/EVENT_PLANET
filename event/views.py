from rest_framework import viewsets
from .models import *
from .serializers import *



class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = Eventserializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
        