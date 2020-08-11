from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from moonvision.users.models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    fieldsets = (('User', {'fields': ('name',)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ['username', 'name', 'is_superuser']
    search_fields = ['name']
