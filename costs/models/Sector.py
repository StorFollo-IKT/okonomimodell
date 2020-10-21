from django.db import models

from . import Application, Customer, Department, Server


class Sector(models.Model):
    name = models.CharField('Navn', max_length=50)
    departments = models.ManyToManyField(Department, verbose_name='Ansvar', blank=True, related_name='sector_dep')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Kunde', related_name='sectors')

    def applications(self):
        apps = Application.objects.filter(
            department__in=self.departments.all()
        )
        return apps

    def servers(self):
        return Server.objects.filter(
            applications__department__in=self.departments.all()
        )

    def costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.cost()
        for delivery in self.deliveries.all():
            cost += delivery.sum()

        return cost

    def external_costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.external_cost

        return cost

    def licence_costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.licence_cost

        return cost

    def server_costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.server_cost()

        return cost

    def __str__(self):
        return '%s %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'Sektor'
        verbose_name_plural = 'Sektorer'
        unique_together = ['name', 'customer']
        ordering = ['name']
