import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import ProtectedError

from ad_import.load_data import LoadUsers
from costs.models import Customer, User

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        customers = Customer.objects.all().values_list('id', flat=True)
        parser.add_argument('--customer', nargs='?',
                            choices=list(customers), help='Kunde')

    def handle(self, *args, **options):
        load = LoadUsers()
        if options['customer']:
            customers = [Customer.objects.get(id=options['customer'])]
        else:
            customers = Customer.objects.all()

        for customer in customers:
            for directory in customer.ad_directories.all():
                print(directory)
                load.connect(directory=directory)
                for query in load.queries:
                    entries = load.run_query(query)
                    for user_data in entries:
                        ad_user = load.load_user(user_data)
                        if not ad_user:
                            continue
                        if ad_user.disabled():
                            ad_user.delete()
                            continue
                        else:
                            try:
                                user = User.objects.get(ad_object=ad_user)
                            except User.DoesNotExist:
                                # print('No user for AD object %s' % ad_user)
                                user = User(ad_object=ad_user)
                            except ProtectedError as e:
                                print(e)
                                continue

                        try:
                            if ad_user.employeeID:
                                user.number = int(ad_user.employeeID)
                            else:
                                user.number = None
                        except ValueError as e:
                            print(e)

                        user.name = ad_user.displayName
                        user.email = ad_user.mail
                        user.ad_object = ad_user
                        user.dn = ad_user.distinguishedName
                        if ad_user.company:
                            try:
                                user_customer = Customer.objects.get(name__iexact=ad_user.company)
                                if user_customer != customer:
                                    print('Company %s matched customer %s' % (ad_user.company, user_customer))
                                    user.customer = user_customer
                            except Customer.DoesNotExist:
                                print('Company %s does not exist as customer' % ad_user.company)
                                user.customer = customer
                        else:
                            user.customer = customer
                        try:
                            user.save()
                        except IntegrityError as e:
                            raise e

                inactive = load.get_inactive()
                for user in inactive:
                    try:
                        user.delete()
                    except ProtectedError:
                        print('Protected relations:', user)
                    except IntegrityError:
                        print('Integrity error:', user)
