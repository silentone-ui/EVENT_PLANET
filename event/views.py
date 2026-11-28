from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from .models import *
from .serializers import *
from core.permissions import *

@method_decorator([vary_on_headers('Authorization'), cache_page(60 * 2)], name='list') 
@method_decorator([vary_on_headers('Authorization'), cache_page(60 * 2)], name='retrieve')
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]

    def get_queryset(self):
        qs = Event.objects.select_related('organizer').prefetch_related(
        'attribute_values__attribute'
        ).order_by('-created_at')
        user = self.request.user
        if user.is_authenticated and getattr(user, 'role', None) == 'organizer':
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
        return Registration.objects.select_related('event', 'user', 'event__organizer').filter(
            Q(user=user) | Q(event__organizer=user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)


class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEventOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Stage.objects.select_related('event','event__organizer').order_by('start_time')
        event_id = self.request.query_params.get('event')
        if event_id:
            qs = qs.filter(event_id=event_id)
        if getattr(user, 'role', None) == 'organizer':
            return qs.filter(Q(event__status=Event.Status.PUBLISHED) | Q(event__organizer=user))
        return qs.filter(event__status=Event.Status.PUBLISHED)

    def perform_create(self, serializer):
        event = serializer.validated_data.get('event')
        if event.organizer != self.request.user:
            raise DRFValidationError('فقط برگزارکننده همان ایونت می‌تواند مرحله بسازد.')
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)


class StageAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = StageAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsEventOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = StageAssignment.objects.select_related('stage', 'user', 'stage__event')
        if getattr(user, 'role', None) == 'organizer':
            return qs.filter(Q(stage__event__organizer=user) | Q(stage__event__status=Event.Status.PUBLISHED))
        return qs.filter(stage__event__status=Event.Status.PUBLISHED)

    def perform_create(self, serializer):
        stage = serializer.validated_data.get('stage')
        if stage.event.organizer != self.request.user:
            raise DRFValidationError('فقط برگزارکننده همان ایونت می‌تواند نقش بدهد.')
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Feedback.objects.select_related('event','user').filter(
            Q(user=user) | Q(event__organizer=user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)

@method_decorator([vary_on_headers('Authorization'), cache_page(60 * 5)], name='list')
@method_decorator([vary_on_headers('Authorization'), cache_page(60 * 5)], name='retrieve')
class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEventOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Result.objects.select_related('event','event__organizer').order_by('-created_at')
        if getattr(user, 'role', None) == 'organizer' and user.is_authenticated:
            return qs.filter(Q(event__organizer=user) | Q(event__status=Event.Status.FINISHED))
        return qs.filter(event__status=Event.Status.FINISHED)

    def perform_create(self, serializer):
        event = serializer.validated_data.get('event')
        if event.organizer != self.request.user:
            raise DRFValidationError('فقط برگزارکننده همان ایونت می‌تواند نتیجه منتشر کند.')
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)

class EventAttributeViewSet(viewsets.ModelViewSet):
    queryset = EventAttribute.objects.all().order_by('name')
    serializer_class =   EventAttributeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

class EventAttributeValueViewSet(viewsets.ModelViewSet):
    serializer_class = EventAttributeValueSerializer
    permission_classes = [permissions.IsAuthenticated, IsEventOwnerOrReadOnly]
    def get_queryset(self):
        qs = EventAttributeValue.objects.select_related('event', 'attribute')
        if getattr(self.request.user, 'role', None) == 'organizer':
            return qs.filter(Q(event__organizer=self.request.user) | Q(event__status=Event.Status.PUBLISHED))
        return qs.filter(event__status=Event.Status.PUBLISHED)
    def perform_create(self, serializer):
        event = serializer.validated_data.get('event')
        if event.organizer != self.request.user:
            raise DRFValidationError('فقط برگزارکننده همان ایونت می‌تواند مقدار بدهد.')
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)