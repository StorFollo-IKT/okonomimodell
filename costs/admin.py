from django.contrib import admin

# Register your models here.
from costs.models import Application, Customer, Department, Product, ProductType, Sector, Server, User, ProductDelivery

admin.site.register(Customer)
admin.site.register(ProductType)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'price']
    list_filter = ['type']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'customer', 'department']
    list_filter = ['name', 'vendor', 'customer', 'department']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'customer', 'last_logon', 'last_update']
    readonly_fields = ['applications_string', 'last_update']
    list_filter = ['customer', 'last_logon', 'imported']


@admin.register(ProductDelivery)
class ProductDeliveryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'amount', 'sum']
    readonly_fields = ['sum']
    list_filter = ['customer', 'product']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'department', 'ad_user', 'number']
    list_filter = ['department__customer', 'department__sector_dep', 'department']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'customer']
    list_filter = ['customer']


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer']
