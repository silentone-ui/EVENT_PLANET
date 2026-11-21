from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'is_staff', 'is_superuser') 
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    search_fields = ('phone',)
    ordering = ('phone',)

admin.site.register(User, CustomUserAdmin)
