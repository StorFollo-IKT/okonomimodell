import json
import os
from django.core.management.base import BaseCommand

from ad_import.load_data import LoadUsers
from ad_import.models import User as ADUser
from costs.models import Customer, Student


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
            file = '/home/datagrunnlag/Elever/students_%s.json' % customer.id
            if not os.path.exists(file):
                continue
            with open(file) as fp:
                data = json.load(fp)
                for ssn, student in data.items():
                    user_data = {
                        'customer': customer,
                        'firstName': student['name']['n']['given'],
                        'lastName': student['name']['n']['family'],
                        'guid': student['userid'][1]
                    }

                    student_obj, created = Student.objects.update_or_create(
                        ssn=ssn,
                        defaults=user_data
                    )

                    try:
                        user = ADUser.objects.get(employeeNumber=ssn)
                        if user.users:
                            user.users.student = student_obj
                            user.users.save()
                    except ADUser.DoesNotExist:
                        print('No user with SSN %s, %s' % ssn, student_obj)
                    except ADUser.MultipleObjectsReturned:
                        print('Multiple users with SSN %s:' % ssn)
                        users = ADUser.objects.filter(employeeNumber=ssn)
                        for user in users:
                            print(user, user.sAMAccountName)
