import datetime

from django.core.management.base import BaseCommand

from ad_import.load_data import LoadUsers
from costs.models import Customer, User

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('customer', nargs='+', type=str)

    def handle(self, *args, **options):
        load = LoadUsers()
        for customer in Customer.objects.all():
            for directory in customer.ad_directories.all():
                print(directory)
                load.connect(directory=directory)
                for query in load.queries:
                    entries = load.run_query(query)
                    for user_data in entries:
                        ad_user = load.load_user(user_data)
                        if not ad_user:
                            continue
                        user, created = User.objects.get_or_create(dn=ad_user.distinguishedName)
                        user.name = ad_user.displayName
                        user.email = ad_user.mail
                        user.ad_object = ad_user
                        user.customer = customer
                        user.save()
