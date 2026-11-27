from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RegistrationViewSet, StageViewSet, StageAssignmentViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', RegistrationViewSet, basename='registration')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'stage-assignments', StageAssignmentViewSet, basename='stage-assignment')

urlpatterns = [
    path('', include(router.urls)),
]