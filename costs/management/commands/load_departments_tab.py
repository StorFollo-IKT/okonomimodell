import datetime
from pprint import pprint
from xml.etree import ElementTree

from django.core.management.base import BaseCommand

from costs.models import Department

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('company', nargs='+', type=str)

    def handle(self, *args, **options):
        file = '/home/datagrunnlag/ansvar_%s.txt' % options['company'][0]
        with open(file, 'r') as fp:
            for line in fp:
                data = line.strip().split("\t")
                # dep = Department(number=data[0], name=data[1], customer_id=options['company'][0])
                dep, created = Department.objects.get_or_create(number=data[0], customer_id=options['company'][0])
                dep.name = data[1]
                dep.save()
