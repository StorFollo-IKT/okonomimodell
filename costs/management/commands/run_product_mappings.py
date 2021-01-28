from django.core.management.base import BaseCommand

from costs.models import Product, ProductMapping, ProductType, User


class Command(BaseCommand):
    def handle(self, *args, **options):
        mappings = ProductMapping.objects.all()
        mapping: ProductMapping
        for mapping in mappings:
            for organisation in mapping.organisations.all():
                print(organisation)
                for employment in organisation.employments.all():
                    try:
                        user = User.objects.get(employee=employment.resource)
                    except User.DoesNotExist:
                        # print('Ingen bruker tilknyttet %s' % employment.resource)
                        continue
                    except User.MultipleObjectsReturned:
                        user = User.objects.filter(employee=employment.resource).first()
                    if user.products.count():
                        status = self.user_has_product_of_type(user, mapping.product.type)
                        if status:
                            continue
                        else:
                            print('Tildel %s til %s orgenhet %s' % (mapping.product, user, organisation))
                            user.products.add(mapping.product)

    def user_has_product_of_type(self, user: User, product_type: ProductType):
        products_of_type = Product.objects.filter(type=product_type)
        for product in products_of_type:
            if product in user.products.all():
                return product
        return None
