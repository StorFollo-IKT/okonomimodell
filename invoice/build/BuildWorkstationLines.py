from django.db import IntegrityError
from django.db.models import QuerySet

from costs.models import Product, Workstation
from invoice.models import Invoice, InvoiceLine


class BuildWorkstationLines:
    @staticmethod
    def build_workstations(workstations: QuerySet, function_fallback: int):
        workstation_count = {}

        workstation: Workstation
        for workstation in workstations.all():
            if not workstation.user:
                # print('%s has no user' % workstation)
                continue
            if not workstation.user.employee:
                print('%s is not employed' % workstation.user)
                continue
            main_position = workstation.user.employee.main_position(assume=True)
            if not main_position:
                print('Main position for %s %s not found' % (workstation.user.employee.resourceId, workstation.user.employee))
                continue

            cost_center = main_position.costCenter
            if not main_position.function:
                function = function_fallback
            else:
                function = main_position.function.value

            if cost_center not in workstation_count:
                workstation_count[cost_center] = {}
            if function not in workstation_count[cost_center]:
                workstation_count[cost_center][function] = []

            workstation_count[cost_center][function].append(workstation)
        return workstation_count

    def build_lines(self, invoice: Invoice, account: str, product_name='Drift av arbeidsstasjon', function_fallback=120):
        if invoice.locked:
            print('Invoice %s is locked' % invoice)
            return
        workstations = Workstation.objects.filter(customer=invoice.customer)
        product = Product.objects.get(name=product_name)

        workstation_count = self.build_workstations(workstations, function_fallback)

        for cost_center, functions in workstation_count.items():
            for function, workstations in functions.items():
                text = 'Drift av %d arbeidsstajon(er)' % len(workstations)

                line = InvoiceLine(
                    invoice=invoice,
                    text=text,
                    account=account,
                    cost_center=cost_center.value,
                    function=function,
                    amount=(product.price * len(workstations)) * 1.25,
                )
                try:
                    line.save()
                except IntegrityError:
                    continue
