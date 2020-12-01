import json

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from ad_import.models import Server, User as ADUser, Directory
from costs.models import Customer, User, Workstation


class WorkstationsSCCM:
    def __init__(self, customer: Customer):
        self.customer = customer
        self.file = '/home/datagrunnlag/SCCM/SCCM_%s.json' % self.customer.id

    def load_json(self):
        with open(self.file, 'r', encoding='latin1') as fp:
            return json.load(fp)

    def save_file(self, string):
        if type(string) == bytes:
            mode = 'wb'
        else:
            mode = 'w'

        with open(self.file, mode) as fp:
            fp.write(string)

    def load(self):
        for workstation in self.load_json():
            try:
                workstation_obj = Workstation.objects.get(
                    serial=workstation['SerialNumber0']
                )
            except Workstation.DoesNotExist:
                workstation_obj = Workstation(serial=workstation['SerialNumber0'])

            workstation_obj.name = workstation['Name0']
            if workstation['Distinguished_Name0']:
                workstation_obj.distinguishedName = workstation['Distinguished_Name0']
                workstation_obj.ad_object = lookup_ad_object(workstation_obj)
            else:
                print('%s has no AD object' % workstation['Name0'])

            workstation_obj.manufacturer = workstation['Manufacturer0']
            workstation_obj.model = workstation['Model0']
            workstation_obj.user_name = workstation['User_Name0']
            workstation_obj.user_domain = workstation['User_Domain0']

            if is_server(workstation_obj):
                continue

            if workstation_obj.user_domain:
                user_directory = lookup_directory(workstation_obj.user_domain)
                if user_directory:
                    workstation_obj.user = lookup_user(user_directory, workstation_obj)

            if workstation_obj.user and workstation_obj.user.customer:
                workstation_obj.customer = workstation_obj.user.customer
            else:
                workstation_obj.customer = self.customer

            workstation_obj.save()


def lookup_directory(directory_name: str) -> Directory:
    try:
        return Directory.find_directory(directory_name)
    except Directory.DoesNotExist:
        print('Directory %s does not exist' % directory_name)


def lookup_ad_object(workstation: Workstation):
    try:
        return workstation.ad_computer_lookup()
    except ObjectDoesNotExist:
        print('AD object with DN %s does not exist' % workstation.distinguishedName)
    except MultipleObjectsReturned:
        print('Multiple objects with DN %s' % workstation.distinguishedName)


def lookup_user(user_domain: Directory, workstation: Workstation):
    try:
        return workstation.user_lookup(user_domain)
    except ADUser.DoesNotExist:
        print(
            'User %s does not exist in domain %s' % (workstation.user_name, user_domain)
        )
    except User.DoesNotExist:
        print(
            'No user is related to %s in domain %s'
            % (workstation.user_name, user_domain)
        )
    except Directory.DoesNotExist:
        pass
        # print('User directory %s does not exist' % workstation.user_domain)


def is_server(workstation: Workstation):
    try:
        Server.objects.get(distinguishedName=workstation.distinguishedName)
        return True
    except Server.DoesNotExist:
        return False
