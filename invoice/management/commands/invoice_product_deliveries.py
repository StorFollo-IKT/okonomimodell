from django.core.management.base import BaseCommand

from costs.models import Customer
from invoice.build import BuildProductDeliveries
from invoice.build import InvoiceUtils


class Command(BaseCommand):
    def add_arguments(self, parser):
        customers = Customer.objects.all().values_list('id', flat=True)
        customers = list(customers)
        parser.add_argument('--customer', nargs='+', choices=customers)

    def handle(self, *args, **options):
        if options['customer'] is None:
            for customer in Customer.objects.all():
                self.run(customer)
        else:
            customer = Customer.objects.get(id=options['customer'])
            self.run(customer)

    @staticmethod
    def run(customer_obj):
        invoice = InvoiceUtils.get_latest_invoice(customer_obj)
        if not invoice:
            return
        BuildProductDeliveries.build_lines(invoice)
