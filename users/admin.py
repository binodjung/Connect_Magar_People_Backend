from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # your custom user model

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Optional: customize which fields show in admin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'mobile_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'email', 'mobile_number', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'full_name', 'email', 'is_staff')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('username',)
