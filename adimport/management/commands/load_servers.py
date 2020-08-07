from datetime import datetime

from django.core.management.base import BaseCommand

from adimport.load_ad import AdLoad
from adimport.models import Workstation
from costs.models import Server

now = datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('customer', nargs='+', type=str)

    def handle(self, *args, **options):
        customer = options['customer'][0]
        AdLoad.run_queries(customer, 'costs.Server', Server)
