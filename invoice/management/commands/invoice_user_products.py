import datetime

from django.core.management.base import BaseCommand

from costs.models import Customer, ProductType
from invoice.build import BuildProductLines
from invoice.models import Invoice


class Command(BaseCommand):
    help = 'Generer fakturalinjer for tjenester knyttet til brukere'

    def add_arguments(self, parser):
        customers = Customer.objects.all().values_list('id', flat=True)
        customers = list(customers)

        product_types = ProductType.objects.all().values_list('type', flat=True)
        product_types = list(product_types)

        parser.add_argument('--customer', nargs='+', choices=customers, help='Kunde')
        parser.add_argument('-t', '--type', nargs='+', choices=product_types, help='Tjenestetype')

    def handle(self, *args, **options):
        if options['customer'] is None:
            customers = Customer.objects.all()
        else:
            customers = []
            for customer in options['customer']:
                customers.append(Customer.objects.get(id=customer))

        if options['type'] is None:
            product_types = ProductType.objects.all().values_list('type', flat=True)
            product_types = list(product_types)
        else:
            product_types = options['type']

        today = datetime.date.today()

        for customer_obj in customers:
            try:
                invoice = Invoice.objects.get(
                    customer=customer_obj, date__year=today.year, date__month=today.month, locked=False
                )
            except Invoice.DoesNotExist:
                print(
                    'No invoice created for %s %s-%s'
                    % (customer_obj, today.year, today.month)
                )
                continue

            for product_type in product_types:
                builder = BuildProductLines()
                builder.build_lines(invoice, type_filter=product_type)
