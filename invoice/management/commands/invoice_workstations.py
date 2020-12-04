from django.core.management.base import BaseCommand

from costs.models import Customer
from invoice.build import BuildWorkstationLines, InvoiceUtils


class Command(BaseCommand):
    def add_arguments(self, parser):
        customers = Customer.objects.all().values_list('id', flat=True)
        parser.add_argument('--customer', nargs='+',
                            choices=list(customers), help='Kunde')

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

        build = BuildWorkstationLines()
        build.build_lines(invoice, '120007')
