import datetime
import os

from django.core.management.base import BaseCommand

from costs.import_utils import WorkstationsSCCM
from costs.models import Customer

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        customers = Customer.objects.all().values_list('id', flat=True)
        parser.add_argument(
            '--customer', nargs='?', choices=list(customers), help='Kunde'
        )

    def handle(self, *args, **options):
        if options['customer'] is None:
            for customer in Customer.objects.all():
                self.run(customer)
        else:
            customer = Customer.objects.get(id=options['customer'])
            self.run(customer)

    @staticmethod
    def run(customer):
        file = '/home/datagrunnlag/SCCM/SCCM_%s.json' % customer.id
        if not os.path.exists(file):
            return

        load = WorkstationsSCCM(customer)
        load.load()
