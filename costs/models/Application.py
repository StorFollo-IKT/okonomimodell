from django.db import models

from . import Customer, Department, Product, Sector, Server, User


class Application(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Kunde', related_name='applications')
    name = models.CharField('Applikasjonsnavn', max_length=100)
    vendor = models.CharField('Leverandør', max_length=100)
    cloud = models.BooleanField('Skytjeneste')
    servers = models.ManyToManyField(Server, verbose_name='Servere', related_name='applications', blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Ansvar')
    sector = models.ForeignKey(Sector, verbose_name='Sektor', on_delete=models.PROTECT,
                               related_name='applications', blank=True, null=True)
    integrations = models.ManyToManyField('self', verbose_name='Integrasjoner', related_name='integrated', blank=True)
    licence_cost = models.IntegerField('Lisenskostnad per år', default=0)
    internal_hours = models.IntegerField('Applikasjonsdrift timer pr mnd', default=0)
    external_cost = models.IntegerField('Konsulentkostnad per år', default=0)
    responsible = models.ForeignKey(User, verbose_name='Systemansvarlig', on_delete=models.PROTECT,
                                    related_name='responsible', blank=True, null=True)
    super_user = models.ForeignKey(User, verbose_name='Superbruker', on_delete=models.PROTECT,
                                   related_name='super_user', blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'applikasjon'
        verbose_name_plural = 'applikasjoner'
        unique_together = ['customer', 'name', 'department']
        ordering = ['customer', 'name']

    def internal_hour_cost(self):
        product = Product.objects.get(name='Drift av applikasjon per time')
        return self.internal_hours * product.price

    def internal_hour_cost_year(self):
        return self.internal_hour_cost() * 12

    def server_cost(self):
        """
        Server cost per month
        :return:
        """
        server_cost = 0
        for server in self.servers.all():
            server_cost += server.application_cost()
        return server_cost

    def server_cost_year(self):
        return self.server_cost() * 12

    def external_cost_total(self):
        """
        Licence and external cost per year
        """
        return self.external_cost + self.licence_cost

    def cost(self):
        """
        Total cost per year
        """
        return self.server_cost_year() + self.external_cost + self.licence_cost

    def internal_cost_total_year(self):
        return self.internal_hour_cost_year() + self.server_cost_year()

    def total_year(self):
        return self.server_cost_year() + self.external_cost_total() + self.internal_hour_cost_year()
