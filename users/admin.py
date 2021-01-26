from .forms import UserChangeForm, UserCreationForm
from django.contrib.auth import admin as auth_admin
from django.contrib import admin
from .models import User, Organization

# Register your models here.
admin.site.register(Organization)

@admin.register(User)
class AdminUser(auth_admin.UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'phone', 'birthdate', 'organization')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    limited_fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {
         'fields': ('name', 'phone', 'birthdate')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = auth_admin.AdminPasswordChangeForm
    list_display = ('id', 'email', 'name', 'organization', 'is_staff')
    list_filter = ('phone', 'organization', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('name', 'email')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined',)
