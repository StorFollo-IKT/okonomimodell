from django.db import models

from . import Customer, Department


class Sector(models.Model):
    name = models.CharField('Navn', max_length=50)
    departments = models.ManyToManyField(Department, verbose_name='Ansvar', blank=True, related_name='sector_dep')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Kunde', related_name='sectors')

    def servers(self):
        from . import Server
        return Server.objects.filter(
            applications__in=self.applications.all()
        )

    def costs(self):
        """
        Costs per year
        """
        cost = 0
        for app in self.applications.all():
            cost += app.cost()
        for delivery in self.deliveries.all():
            cost += delivery.sum_year()

        return cost

    def external_costs(self):
        """
        External cost per year
        """
        cost = 0
        for app in self.applications.all():
            cost += app.external_cost

        return cost

    def licence_costs(self):
        """
        Licence cost per year
        """
        cost = 0
        for app in self.applications.all():
            cost += app.licence_cost

        return cost

    def server_costs(self):
        """
        Server cost per year
        """
        cost = 0
        for app in self.applications.all():
            cost += app.server_cost_year()

        return cost

    def __str__(self):
        return '%s %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'Sektor'
        verbose_name_plural = 'Sektorer'
        unique_together = ['name', 'customer']
        ordering = ['name']
