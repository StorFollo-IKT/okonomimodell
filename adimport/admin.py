from django.contrib import admin

# Register your models here.
from adimport.models import Directory, Group, Query, Workstation


@admin.register(Directory)
class DirectoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'dc', 'dn']


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ['directory', 'query', 'base_dn', 'type', 'target']
    list_filter = ['directory', 'type', 'target']
    save_as = True


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['directory', 'application', 'dn']
    save_as = True


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'name', 'last_update']
    list_filter = ['customer', 'last_logon']
