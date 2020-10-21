from django.db import models

from . import Product


class ProductGroup(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, verbose_name='Tjenester', related_name='product_groups')

    def sum_year(self):
        total = 0
        for line in self.products.all():
            total += line.sum_year()

        return total

    class Meta:
        verbose_name = 'Tjenestegruppe'
        verbose_name_plural = 'Tjenestegrupper'
        ordering = ['name']
