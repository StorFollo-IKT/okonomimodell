import os
from django.core.management.base import BaseCommand

from costs.import_utils import M365License, M365Exception
from costs.models import Customer


# https://docs.microsoft.com/en-us/azure/active-directory/enterprise-users/licensing-service-plan-reference


class Command(BaseCommand):
    def handle(self, *args, **options):
        m365 = M365License()

        for customer in Customer.objects.all():
            print(customer)
            file = os.path.join('/', 'home', 'datagrunnlag', 'M365_%s.csv' % customer.id)
            if not os.path.exists(file):
                continue
            user_products = m365.load_file(file)
            for upn, user_product_names in user_products.items():
                try:
                    user = m365.find_user(upn, customer)
                except M365Exception as e:
                    print('\t%s' % e)
                    continue

                m365.product_cleanup(user, user_product_names)
                m365.products_add(user, user_product_names)

                # for product_name in user_product_names:
                #     if product_name in m365.product_mappings:
                #         product = m365.product_mappings[product_name]
                #         user.products.add(product)
