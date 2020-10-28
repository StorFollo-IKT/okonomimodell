from django.db import models
from django.db.models import Sum
from employee_info.models import Company, CostCenter, Function

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

    def is_valid(self):
        lines = self.objects.filter(application=self.application)
        percent_sum = lines.aggregate(Sum('percentage'))['percentage__sum']
        return percent_sum == 100

    def customer(self):
        return self.application.customer
