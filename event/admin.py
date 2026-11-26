from django.contrib import admin
from .models import *


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    fields = ('user', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'organizer', 'capacity')
    readonly_fields = ('id',)
    list_filter = ('status',)
    search_fields = ('title',)
    exclude = ('participants',)
    inlines = [RegistrationInline]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'created_at')
    list_filter = ('event',)


@admin.register(EventAttribute)
class EventAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'event', 'value')