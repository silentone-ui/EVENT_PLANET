from django.contrib import admin
from .models import *


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    fields = ('user', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user',)


class StageInline(admin.TabularInline):
    model = Stage
    extra = 0
    fields = ('title', 'start_time', 'end_time')


class StageAssignmentInline(admin.TabularInline):
    model = StageAssignment
    extra = 0
    autocomplete_fields = ('user',)


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    fields = ('user', 'rating', 'comment')
    readonly_fields = ('created_at',)


class ResultInline(admin.StackedInline):
    model = Result
    extra = 0
    fields = ('title', 'description')
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'organizer', 'capacity')
    list_filter = ('status',)
    search_fields = ('title',)
    inlines = [StageInline, RegistrationInline,FeedbackInline,ResultInline]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'start_time', 'end_time')
    list_filter = ('event',)
    search_fields = ('title',)
    inlines = [StageAssignmentInline]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'created_at')
    list_filter = ('event',)


@admin.register(StageAssignment)
class StageAssignmentAdmin(admin.ModelAdmin):
    list_display = ('stage', 'user', 'role')
    list_filter = ('role',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'created_at')
    list_filter = ('event', 'rating')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('event', 'title', 'created_at')
    search_fields = ('title', 'event__title')



@admin.register(EventAttribute)
class EventAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'event', 'value','value_display')
    list_select_related = ('attribute', 'event')
    list_filter = ('attribute',)
    search_fields = ('event__title', 'attribute__name')

    @admin.display(description='مقدار')
    def value_display(self, obj):
        return obj.value
