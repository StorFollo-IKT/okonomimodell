import csv
import datetime
import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from ad_import.models import Directory
from ad_import.models import Server, User as ADUser
from costs.models import Customer, User
from costs.models.Workstation import Workstation

now = datetime.datetime.now()


class Command(BaseCommand):
    def handle(self, *args, **options):
        for customer in Customer.objects.all():
            data_file = '/home/datagrunnlag/SCCM_%s.csv' % customer.id
            if not os.path.exists(data_file):
                continue

            with open(data_file, newline='') as fp:
                csv_reader = csv.DictReader(
                    fp,
                    delimiter=';',
                    fieldnames=[
                        'SerialNumber',
                        'Manufacturer',
                        'Model',
                        'Name',
                        'User_Name',
                        'User_Domain',
                        'Creation_Date',
                        'Last_Logon_Timestamp',
                        'Distinguished_Name',
                        'Full_Domain_Name',
                    ],
                )

                for row in csv_reader:
                    key: str
                    for key, value in row.items():
                        if value == 'NULL':
                            row[key] = None

                    try:
                        workstation = Workstation.objects.get(
                            serial=row['SerialNumber']
                        )
                    except Workstation.DoesNotExist:
                        workstation = Workstation(
                            name=row['Name'],
                            distinguishedName=row['Distinguished_Name'],
                            manufacturer=row['Manufacturer'],
                            model=row['Model'],
                            serial=row['SerialNumber'],
                            user_name=row['User_Name'],
                            user_domain=row['User_Domain'],
                            customer=customer,
                        )

                    if workstation.distinguishedName:
                        try:
                            ad_object = workstation.ad_computer_lookup()
                            workstation.ad_object = ad_object
                        except ObjectDoesNotExist:
                            try:
                                workstation_domain = Directory.objects.get(
                                    name__iexact=row['Full_Domain_Name']
                                )
                                try:
                                    Server.objects.get(
                                        distinguishedName=workstation.distinguishedName
                                    )
                                except Server.DoesNotExist:
                                    print(
                                        'Workstation DN %s does not exist in domain %s'
                                        % (
                                            workstation.distinguishedName,
                                            workstation_domain,
                                        )
                                    )
                            except Directory.DoesNotExist:
                                pass
                    else:
                        print('Workstation %s has no DN' % workstation.name)

                    if workstation.user_name:
                        try:
                            user_domain = Directory.objects.get(
                                name__istartswith=workstation.user_domain
                            )
                            # print(ADUser.objects.get(sAMAccountName__iexact=workstation.user_name, directory=user_domain))
                            workstation.user = workstation.user_lookup(user_domain)
                            # break
                        except ADUser.DoesNotExist:
                            print(
                                'User %s does not exist in domain %s'
                                % (workstation.user_name, user_domain)
                            )
                            # break
                        except User.DoesNotExist:
                            print(
                                'No user is related to %s in domain %s'
                                % (workstation.user_name, user_domain)
                            )
                            break
                        except Directory.DoesNotExist:
                            pass
                            # print('User directory %s does not exist' % workstation.user_domain)
                    workstation.save()
