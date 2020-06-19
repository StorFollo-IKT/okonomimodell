from django.contrib import admin

# Register your models here.
from costs.models import Application, Customer, Department, Product, ProductType, Sector, Server, User, ProductDelivery

admin.site.register(Customer)
admin.site.register(ProductType)
admin.site.register(Product)
admin.site.register(Department)
admin.site.register(User)
admin.site.register(Sector)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'customer', 'department']
    list_filter = ['name', 'vendor', 'customer', 'department']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'customer', 'last_logon']
    readonly_fields = ['applications_string']
    list_filter = ['customer', 'last_logon']


@admin.register(ProductDelivery)
class ProductDeliveryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'amount', 'sum']
    readonly_fields = ['sum']
    list_filter = ['customer', 'product']
