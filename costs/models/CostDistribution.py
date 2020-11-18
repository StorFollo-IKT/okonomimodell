from django.db import models
from employee_info.models import CostCenter, Function

from . import Application


class CostDistribution(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name='applikasjon',
                                    related_name='distributions')
    percentage = models.IntegerField(verbose_name='prosent')

    account = models.CharField('konto', max_length=6)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.PROTECT, blank=True, null=True,
                                    verbose_name='ansvar')
    function = models.ForeignKey(Function, on_delete=models.PROTECT, verbose_name='funksjon')

    class Meta:
        unique_together = ['application', 'account', 'cost_center', 'function']
        verbose_name = 'kostnadsfordeling'
        verbose_name_plural = 'kostnadsfordelinger'

    def __str__(self):
        return '%s%% of %skr = %skr' % (
            self.percentage, self.application.total_year(), self.amount())

    def customer(self):
        return self.application.customer

    def amount(self):
        return self.application.cost() * (self.percentage/100)
