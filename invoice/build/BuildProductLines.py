from django.db import IntegrityError
from typing import Dict, List

from costs.models import Product, User
from invoice.models import Invoice, InvoiceLine


class BuildProductLines:
    def build_lines(self, invoice: Invoice, type_filter: str = None, account: str = '119520'):
        if invoice.locked:
            print('Invoice %s is locked' % invoice)
            return

        products = self.get_products(invoice.customer, type_filter)
        for product, cost_centers in products.items():
            for cost_center, functions in cost_centers.items():
                for function, users in functions.items():
                    text = '%s for %d bruker(e)' % (product.name, len(users))
                    if function is None:
                        function = 0

                    line = InvoiceLine(
                        invoice=invoice,
                        text=text,
                        account=account,
                        cost_center=cost_center,
                        function=function,
                        amount=(product.price * len(users)) * 1.25,
                    )
                    try:
                        line.save()
                    except IntegrityError:
                        continue

    @staticmethod
    def product_users(customer, product) -> Dict[str, Dict[str, List[User]]]:
        users = {}
        user_objs = product.users.filter(customer=customer)
        user: User
        for user in user_objs:
            if not user.employee:
                print('%s is not employed' % user)
                continue
            employment = user.employee.main_position()
            if not employment:
                print('%s has no main position' % user)
                continue
            cost_center = employment.costCenter.value
            if employment.function:
                function = employment.function.value
            else:
                function = None

            if cost_center not in users:
                users[cost_center] = {}
            if function not in users[cost_center]:
                users[cost_center][function] = []
            users[cost_center][function].append(user)

        return users

    def get_products(self, customer, type_filter: str = None):
        products = Product.objects.exclude(users=None)
        if type_filter:
            products = Product.objects.filter(type__type=type_filter)
        users = {}
        for product in products:
            users[product] = self.product_users(customer, product)
        return users
