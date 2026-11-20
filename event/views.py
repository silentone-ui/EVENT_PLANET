from rest_framework import viewsets
from .models import *
from .serializers import *
from django.contrib.auth import get_user_model
from core.permissions import IsOrganizerOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = Eventserializer
    permission_classes = [IsOrganizerOrReadOnly]
    

    def perform_create(self, serializer):
        User=get_user_model()
        user = User.objects.first()

        if user:
            serializer.save(organizer=user)
        else:
            raise ValueError("هیچ کاربری در دیتابیس پیدا نشد. لطفاً ابتدا یک کاربر در ادمین بسازید.")
