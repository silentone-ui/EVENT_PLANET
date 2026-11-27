from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', RegistrationViewSet, basename='registration')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'stage-assignments', StageAssignmentViewSet, basename='stage-assignment')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')
router.register(r'results', ResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls)),
]