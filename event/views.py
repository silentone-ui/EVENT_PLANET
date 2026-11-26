from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer
from core.permissions import IsOrganizerOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'organizer':
            return Event.objects.filter(
                Q(status=Event.Status.PUBLISHED) | Q(organizer=user)
            ).order_by('-created_at')
        return Event.objects.filter(status=Event.Status.PUBLISHED).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        event = self.get_object()
        if event.organizer != request.user:
            return Response({'detail': 'فقط برگزارکننده خودش می‌تواند وضعیت را عوض کند.'}, status=403)

        new_status = request.data.get('status')
        valid = [c[0] for c in Event.Status.choices]
        if new_status not in valid:
            return Response({'detail': f'وضعیت باید یکی از {valid} باشد.'}, status=400)

        if not event.can_transition_to(new_status):
            return Response(
                {'detail': f'تغییر از {event.status} به {new_status} مجاز نیست.'},
                status=400
            )

        event.status = new_status
        try:
            event.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)

        return Response(EventSerializer(event).data)


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Registration.objects.filter(
            Q(user=user) | Q(event__organizer=user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)