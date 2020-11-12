from django.contrib import admin

from invoice.models import Invoice, InvoiceLine


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['date', 'customer']
    readonly_fields = ['total', 'locked']


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'text', 'amount']
