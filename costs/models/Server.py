from django.db import models

from ad_import.models import Server as ADServer
from . import Customer, Product


class Server(models.Model):
    name = models.CharField('Navn', max_length=50)
    dns_name = models.CharField('DNS-navn', max_length=100, null=True, blank=True)
    dn = models.CharField('DN', max_length=200, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True, default=None)
    description = models.CharField('Beskrivelse', max_length=100, null=True, blank=True)
    last_logon = models.DateTimeField('Sist aktiv', null=True, blank=True)
    last_update = models.DateTimeField('Sist oppdatert', auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='servers', verbose_name='Tjeneste',
                                null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Kunde', related_name='servers')
    imported = models.BooleanField(default=False)
    ad_object = models.OneToOneField(ADServer, on_delete=models.CASCADE, null=True, blank=True, default=None,
                                     verbose_name='AD')

    class Meta:
        unique_together = ['name', 'customer']
        verbose_name = 'server'
        verbose_name_plural = 'servere'
        ordering = ['customer', 'name']

    def __str__(self):
        value = '%s: %s' % (self.customer, self.name)
        if self.product:
            value += ' (%s)' % self.product
        return value

    def applications_string(self):
        apps_string = ''
        for app in self.applications.all():
            apps_string += str(app) + "\n"

        return apps_string

    def application_cost(self):
        """
        Application cost per month
        :return:
        """

        if not self.product or not self.product.price or self.applications.count() == 0:
            return 0
        return round(self.product.price / self.applications.count())
