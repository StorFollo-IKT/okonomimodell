from django.db import models

from . import Customer, Product, Sector


class ProductDelivery(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='Kunde', on_delete=models.PROTECT, related_name='deliveries')
    product = models.ForeignKey(Product, verbose_name='Tjeneste', on_delete=models.PROTECT, related_name='deliveries')
    amount = models.IntegerField(verbose_name='Antall')
    sector = models.ForeignKey(Sector, verbose_name='Sektor', on_delete=models.PROTECT, related_name='deliveries',
                               blank=True, null=True)

    class Meta:
        verbose_name = 'tjenesteleveranse'
        verbose_name_plural = 'tjenesteleveranser'
        unique_together = ['customer', 'product']

    def __str__(self):
        return '%s %s' % (self.customer, self.product)

    def sum(self):
        """
        Cost per month
        :return:
        """
        return self.product.price * self.amount

    def sum_year(self):
        """
        Cost per year
        :return:
        """
        return self.sum() * 12
