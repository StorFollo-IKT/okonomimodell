import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from ad_import.load_data import LoadServers
from costs.models import Customer, Server

now = datetime.datetime.now()


class Command(BaseCommand):
    def handle(self, *args, **options):
        load = LoadServers()
        for customer in Customer.objects.all():
            for directory in customer.ad_directories.all():
                print(directory)
                load.connect(directory=directory)
                for query in load.queries:
                    entries = load.run_query(query)
                    for server_data in entries:
                        ad_object = load.load_object(server_data)
                        if not ad_object:
                            continue

                        try:
                            server = Server.objects.get(ad_object=ad_object)
                            if ad_object.disabled():
                                server.delete()
                                continue
                        except Server.DoesNotExist:
                            try:
                                server = Server.objects.get(name=ad_object.name)
                            except Server.DoesNotExist:
                                server = Server(ad_object=ad_object)
                        except Server.MultipleObjectsReturned:
                            print('Multiple matches:', ad_object)
                            continue

                        server.dn = ad_object.distinguishedName
                        server.name = ad_object.name
                        server.ad_object = ad_object
                        server.customer = customer
                        server.imported = True
                        server.last_logon = ad_object.lastLogon
                        try:
                            server.save()
                        except IntegrityError as e:
                            print(server)
                            print(e)
