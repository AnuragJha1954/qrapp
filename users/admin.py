from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'verified', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'verified')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'phone_number', 'verified')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'verified', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

# Register the custom admin model
admin.site.register(CustomUser, CustomUserAdmin)
