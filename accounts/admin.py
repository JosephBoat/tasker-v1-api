from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'name', 'is_staff')
    
    # Fields to use when editing users
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields to use when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    # Field to use for ordering
    ordering = ('email',)
    
    # Field to use for searching
    search_fields = ('email', 'name')

# Register your custom User model with your custom UserAdmin
admin.site.register(User, CustomUserAdmin)