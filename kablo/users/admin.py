from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from kablo.users.models import Group, User

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
