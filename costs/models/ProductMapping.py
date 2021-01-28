from django.db import models

from costs.models import Product
from employee_info.models import Organisation


class ProductMapping(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='mapping', verbose_name='tjeneste')
    organisations = models.ManyToManyField(Organisation, related_name='product_mapping',
                                           verbose_name='organisasjonsenheter')

    class Meta:
        verbose_name = 'tjenestetilknytning'
        verbose_name_plural = 'tjenestetilknytninger'
