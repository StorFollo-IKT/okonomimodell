import datetime

from django.core.management.base import BaseCommand

from costs.models import Customer
from invoice.build import BuildProductLines
from invoice.models import Invoice


class Command(BaseCommand):
    def handle(self, *args, **options):
        customer = 'AK'
        customer_obj = Customer.objects.get(id=customer)
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
        builder = BuildProductLines()
        builder.build_lines(invoice)
