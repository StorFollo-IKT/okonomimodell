import datetime
from django.db import models

from ad_import.models import Directory


class Customer(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField('Navn', max_length=50)
    served_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Driftes av')
    ad_directories = models.ManyToManyField(Directory)

    class Meta:
        verbose_name = 'kunde'
        verbose_name_plural = 'kunder'

    def __str__(self):
        return self.name

    def costs(self):
        cost = 0
        for application in self.applications.all():
            cost += application.cost()
        for product in self.deliveries.all():
            cost += product.sum()

        return cost

    def servers_active(self, days=90):
        return self.servers.filter(last_logon__gte=datetime.datetime.today() - datetime.timedelta(days=days))

    def workstations_active(self, days=90):
        return self.workstations.filter(last_logon__gte=datetime.datetime.today() - datetime.timedelta(days=days))

    def users(self):
        from . import User
        return User.objects.filter(department__customer=self)
