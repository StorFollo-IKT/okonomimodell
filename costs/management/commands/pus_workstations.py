from typing import Optional

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from costs.models import Workstation, Customer
from employee_info.models import CostCenter, Function

customers = {
    9: Customer.objects.get(id='FK'),
    10: Customer.objects.get(id='VK'),
    11: Customer.objects.get(id='AK'),
    196: Customer.objects.get(id='SFI'),
    225: Customer.objects.get(id='KF'),
    226: Customer.objects.get(id='BB'),
}

status = {
    12: 'Lager',
    21: 'Feilmeldt',
    30: 'Forsvunnet/stjålet',
    32: 'Ikke meldt ut i PUS',
    33: 'Kassert',
}


def get_customer(pus_workstation) -> Optional[Customer]:
    pus_customer = pus_workstation['assets_UDF_95_Firma_32__40_kommune_47_IKS_47_kunde_41_ItemId']
    pus_id = pus_workstation['id']
    if not pus_customer:
        print('%s har ikke kunde' % pus_id)
        return

    if pus_customer not in customers:
        print('Ukjent kundeid for ressurs %d: %s' % (pus_id, pus_customer))
        return

    return customers[pus_customer]


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

            customer = get_customer(workstation)
            if customer.id != 'SFI':
                workstation_obj.customer = customer
            else:
                if workstation_obj.user and workstation_obj.user.customer:
                    print('%s er registrert med kunde StorFollo IKT, men bruker overstyrer til %s' % (
                    workstation_obj, workstation_obj.user.customer))
                    workstation_obj.customer = workstation_obj.user.customer
                else:
                    workstation_obj.customer = None
                    workstation_obj.cost_center = None
                    workstation_obj.function = None
                    workstation_obj.save()
                    print('%s er er registrert med kunde StorFollo IKT, men har ikke aktiv bruker' % workstation_obj)
                    continue

            if workstation['assets_UDF_95_Eie_47_LeieItemId'] == 202:
                workstation_obj.leased = False
            elif workstation['assets_UDF_95_Eie_47_LeieItemId'] == 203:
                workstation_obj.leased = True
            elif workstation['assets_UDF_95_Eie_47_LeieItemId'] is not None:
                print('Ugyldig verdi for eie/leie: %s' % workstation['assets_UDF_95_Eie_47_LeieItemId'])

            if pus_customer:
                if pus_customer not in customers:
                    print('Ukjent kundeid for ressurs %d: %s' % (workstation_obj.pus_id, pus_customer))

                customer = customers[pus_customer]
                if not customer.company:
                    print('Kunde %s er ikke knyttet mot firma' % customer)
                    continue

            if workstation_obj.customer and workstation_obj.customer.company is not None:
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
            else:
                # print('Kunde %s er ikke knyttet mot firma (ressurs %s)' % (customer, workstation_obj.pus_id))
                workstation_obj.cost_center = None
                workstation_obj.function = None

            workstation_obj.save()
