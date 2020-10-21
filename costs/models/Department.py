from django.core.exceptions import MultipleObjectsReturned
from django.db import models

from costs.models import Customer


class Department(models.Model):
    number = models.IntegerField('Ansvar')
    name = models.CharField('Navn', max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='departments')

    class Meta:
        unique_together = ['number', 'customer']
        verbose_name = 'ansvar'
        verbose_name_plural = 'ansvar'
        ordering = ['name']

    def __str__(self):
        return '%s (%s)' % (self.name, self.customer)

    def sector(self):  # TODO: Rewrite all references to this to application.sector
        try:
            return self.sector_dep.get(departments__number=self.number)
        except MultipleObjectsReturned as e:
            print(e)
            print('Department %s matched multiple sectors:' % self)
            sectors = self.sector_dep.filter(departments__number=self.number)
            for sector in sectors:
                print(sector)
            return sectors.first()
