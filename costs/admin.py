from django.contrib import admin

# Register your models here.
from costs.models import Application, CostDistribution, Customer, Department, Product, ProductDelivery, ProductGroup, \
    ProductMapping, ProductType, Sector, Server, User, ServerType, Workstation, Student

admin.site.register(Customer)
admin.site.register(ProductType)
admin.site.register(ServerType)


class HasAdFilter(admin.SimpleListFilter):
    title = 'har objekt i AD'
    parameter_name = 'has_ad'

    def lookups(self, request, model_admin):
        return [('true', 'Ja'), ('false', 'Nei')]

    def queryset(self, request, queryset):
        if self.value() == 'false':
            return queryset.filter(ad_object=None)
        if self.value() == 'true':
            return queryset.exclude(ad_object=None)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'price', 'user_count']
    list_filter = ['type']


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ['sum_year']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'customer', 'sector']
    list_filter = ['name', 'vendor', 'customer', 'sector']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'product', 'customer', 'last_logon', 'last_update']
    readonly_fields = ['applications_string', 'last_update']
    list_filter = ['customer', 'ad_object__directory', 'type', 'ad_object__lastLogon', 'imported', HasAdFilter]


@admin.register(ProductDelivery)
class ProductDeliveryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'amount', 'sum', 'account']
    readonly_fields = ['sum']
    list_filter = ['customer', 'account', 'product__type', 'product']


class IsEmployeeFilter(admin.SimpleListFilter):
    title = 'er ansatt'
    parameter_name = 'is_employee'

    def lookups(self, request, model_admin):
        return [('true', 'Ja'), ('false', 'Nei')]

    def queryset(self, request, queryset):
        if self.value() == 'false':
            return queryset.filter(employee=None)
        if self.value() == 'true':
            return queryset.exclude(employee=None)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_select_related = ['ad_object']
    list_display = ['name', 'customer', 'department', 'employee', 'username', 'number', 'last_update', 'last_logon']
    list_filter = ['ad_object__directory', 'customer', 'ad_object__lastLogon', 'ad_object__last_update', HasAdFilter,
                   IsEmployeeFilter]
    readonly_fields = ['company', 'employee', 'display_name']


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_select_related = ['ad_object']
    list_display = ['name', 'manufacturer', 'model', 'owner_display_name', 'user_display_name', 'cost_center',
                    'function', 'last_logon', 'last_logon_ad']
    list_filter = ['ad_object__directory', 'ad_object__lastLogon', 'ad_object__operatingSystem', 'customer',
                   'manufacturer', 'model']
    readonly_fields = ['ad_object', 'user']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'customer']
    list_filter = ['customer']


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer']


@admin.register(CostDistribution)
class CostDistributionAdmin(admin.ModelAdmin):
    list_display = ['application', 'cost_center']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'firstName', 'lastName']
    list_filter = ['customer']


@admin.register(ProductMapping)
class ProductMappingAdmin(admin.ModelAdmin):
    list_display = ['product']
