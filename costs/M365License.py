import csv

from costs.models import Product, User, Customer


class M365Exception(Exception):
    pass


class M365License:
    # https://docs.microsoft.com/en-us/azure/active-directory/enterprise-users/licensing-service-plan-reference
    mappings = {'M365EDU_A3_STUUSEBNFT': None,
                'M365EDU_A3_FACULTY': None,
                'OFFICESUBSCRIPTION_FACULTY': None,
                'STANDARDWOFFPACK_FACULTY': None,
                'STANDARDWOFFPACK_STUDENT': None,
                'STANDARDPACK': 'Microsoft Office 365 E1',
                'STREAM': None,
                'INTUNE_A': 'Microsoft Intune',
                'INTUNE_EDU': None,
                'FLOW_FREE': None,
                'POWER_BI_STANDARD': None,
                'POWER_BI_PRO_FACULTY': None,
                'OFFICESUBSCRIPTION_STUDENT': None,
                'ENTERPRISEPACK': 'Microsoft Office 365 E3',
                'AAD_BASIC': 'Microsoft Azure Active Directory Basic',
                'AAD_PREMIUM': 'Microsoft Azure Active Directory Premium P1',
                'DESKLESSPACK': 'Microsoft Office 365 F3',
                'VISIOCLIENT': 'Microsoft Visio Plan 2',
                'SPE_E3': 'Microsoft 365 E3',
                'EMS': 'Microsoft Enterprise Mobility + Security E3',
                'PROJECT_P1': 'Microsoft Project Plan 1',
                }
    mappings_id = {'4ef96642-f096-40de-a3e9-d83fb2f90211': 'Office 365 Advanced Threat Protection (Plan 1)',
                   '061f9ace-7d42-4136-88ac-31dc755f143f': 'Microsoft Intune',
                   'c5928f49-12ba-48f7-ada3-0d743a3601d5': 'Microsoft Visio Plan 2'
                   }

    @property
    def product_mappings(self):
        product_mappings = {}
        for sku, product_name in {**self.mappings, **self.mappings_id}.items():
            if product_name is None:
                continue
            try:
                product_mappings[product_name] = Product.objects.get(name=product_name)
            except Product.DoesNotExist:
                raise M365Exception('No product named %s' % product_name)
        return product_mappings

    def get_product_name(self, sku_name: str = None, sku_id: str = None):
        if sku_name and sku_name in self.mappings:
            return self.mappings[sku_name]
        elif sku_id and sku_id in self.mappings_id:
            return self.mappings_id[sku_id]
        else:
            raise M365Exception('Unknown SKU: %s/%s' % (sku_name, sku_id))

    def product_cleanup(self, user: User, product_names: list):
        for product in self.product_mappings.values():
            has_product = user.has_product(product)
            should_have = product.name in product_names
            if has_product and not should_have:
                print('Remove %s from %s' % (product, user))
                user.products.remove(product)

    def products_add(self, user: User, product_names: list):
        for product_name in product_names:
            product = self.product_mappings[product_name]
            user.products.add(product)

    @staticmethod
    def find_user(upn: str, customer: Customer) -> User:
        try:
            return User.objects.get(ad_object__userPrincipalName=upn)
        except User.DoesNotExist:
            username, domain = upn.split('@')
            if domain.find('onmicrosoft.com') > -1:
                try:
                    return User.objects.get(ad_object__sAMAccountName=username, customer=customer)
                except User.DoesNotExist:
                    raise M365Exception('No match for sAMAccountName %s' % username)
            else:
                raise M365Exception('No user with UPN %s' % upn)

    def load_file(self, file):
        products = {}
        with open(file, newline='', encoding='utf-8-sig') as fp:
            reader = csv.reader(fp, quotechar='"', delimiter=';')
            headers = next(reader, None)

            for row in reader:
                upn = row[0]
                sku_id = row[1]
                sku = row[2]

                product_name = self.get_product_name(sku, sku_id)

                if product_name is None:
                    continue

                if upn not in products:
                    products[upn] = []

                products[upn].append(product_name)
        return products
