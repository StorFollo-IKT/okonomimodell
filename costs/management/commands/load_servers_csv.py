from datetime import datetime
from pprint import pprint
from xml.etree import ElementTree

from django.core.management.base import BaseCommand

from costs.ad_utils import microsoft_timestamp_to_unix
from costs.models import Department, Server, Customer
import csv


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('company', nargs='+', type=str)

    def handle(self, *args, **options):
        # customer= options['company'][0]
        customer = Customer.objects.get(id=options['company'][0])
        file = '/home/datagrunnlag/servere_AD_%s.csv' % options['company'][0]
        fields = None
        update_time = datetime.now()
        with open(file, 'r', encoding='utf16') as fp:
            csv_reader = csv.reader(fp, delimiter=',')
            for row in csv_reader:
                # data = line.strip().split(',')
                if not fields:
                    fields = row
                    continue

                data = dict(zip(fields, row))
                try:
                    server = Server.objects.get(name__iexact=data['cn'], customer=customer)
                except Server.DoesNotExist:
                    server = Server(name=data['cn'], customer=customer)

                server.name = data['cn']
                server.dns_name = data['dNSHostName']
                server.description = data['description']
                server.dn = data['distinguishedName']
                try:
                    if data['lastLogon'] != '':
                        timestamp = microsoft_timestamp_to_unix(int(data['lastLogon']))
                        last_logon = datetime.fromtimestamp(timestamp)
                    else:
                        last_logon = None
                except TypeError as e:
                    print(e)
                    pprint(data)
                    continue
                server.last_logon = last_logon
                server.save()
