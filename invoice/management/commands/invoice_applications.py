import datetime

from django.core.management.base import BaseCommand

from costs.models import Customer
from invoice.build.BuildApplicationLines import BuildApplicationLines
from invoice.models import Invoice


class Command(BaseCommand):
    def add_arguments(self, parser):
        customers = Customer.objects.all().values_list('id', flat=True)
        customers = list(customers)
        customers.append('all')
        parser.add_argument('customer', type=str, choices=customers)

    def handle(self, *args, **options):
        if options['customer'] == 'all':
            for customer in Customer.objects.all():
                self.run(customer)
        else:
            customer = Customer.objects.get(id=options['customer'])
            self.run(customer)

    @staticmethod
    def run(customer_obj):
        today = datetime.date.today()
        try:
            invoice = Invoice.objects.get(
                customer=customer_obj, date__year=today.year, date__month=today.month
            )
        except Invoice.DoesNotExist:
            print(
                'No invoice created for %s %s-%s'
                % (customer_obj, today.year, today.month)
            )
            return
        builder = BuildApplicationLines()
        builder.build_lines(invoice)
