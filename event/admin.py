from django.contrib import admin
from .models import *

@admin.register(EventAttribute)
class EventAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'organizer')

@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'event', 'value')
