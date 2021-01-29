import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from costs.models import Workstation, Customer
from employee_info.models import CostCenter, Function


class Command(BaseCommand):
    def handle(self, *args, **options):
        headers = {'user-agent': 'StorFollo IKT okonomimodell', 'X-Authorization-Key': settings.PUS_API_KEY}

        customers = {
            9: Customer.objects.get(id='FK'),
            10: Customer.objects.get(id='VK'),
            11: Customer.objects.get(id='AK'),
            196: Customer.objects.get(id='SFI'),
        }

        response = requests.get(settings.PUS_URL + '/agent/api/asset', headers=headers)
        workstations = response.json()
        for workstation in workstations['assets']:
            try:
                workstation_obj = Workstation.objects.get(serial=workstation['uniqueId'])
            except Workstation.DoesNotExist:
                continue

            workstation_obj.pus_id = workstation['id']
            workstation_obj.save()

            pus_customer = workstation['assets_UDF_95_Firma_32__40_kommune_47_IKS_47_kunde_41_ItemId']

            if pus_customer:
                if pus_customer not in customers:
                    print('Ukjent kundeid for ressurs %d: %s' % (workstation_obj.pus_id, pus_customer))

                customer = customers[pus_customer]
                if not customer.company:
                    print('Kunde %s er ikke knyttet mot firma' % customer)
                    continue

                if workstation['assets_UDF_95_Ansvar'] is not None and \
                        len(workstation['assets_UDF_95_Ansvar']) == 3 and \
                        workstation['assets_UDF_95_Funksjon'] == '' and \
                        len(workstation['assets_UDF_95_Kommentar']) == 4:
                    workstation['assets_UDF_95_Funksjon'] = workstation['assets_UDF_95_Ansvar']
                    workstation['assets_UDF_95_Ansvar'] = workstation['assets_UDF_95_Kommentar']

                if workstation['assets_UDF_95_Ansvar']:
                    try:
                        cost_center = CostCenter.objects.get(
                            value=workstation['assets_UDF_95_Ansvar'],
                            company=customer.company)
                        workstation_obj.cost_center = cost_center
                    except CostCenter.DoesNotExist:
                        print('Ugyldig ansvar på ressurs %d %s: %s' % (
                            workstation_obj.pus_id,
                            customer.company,
                            workstation['assets_UDF_95_Ansvar']))
                else:
                    workstation_obj.cost_center = None

                if workstation['assets_UDF_95_Funksjon']:
                    try:
                        function = Function.objects.get(
                            value=workstation['assets_UDF_95_Funksjon'],
                            company=None)
                        workstation_obj.function = function
                    except Function.DoesNotExist:
                        print('Ugyldig funksjon ressurs %d %s: %s' % (
                            workstation_obj.pus_id,
                            customer.company,
                            workstation['assets_UDF_95_Funksjon']))
                else:
                    workstation_obj.function = None

                workstation_obj.save()
