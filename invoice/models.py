from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models

from costs.models import Customer


class Invoice(models.Model):
    date = models.DateField('dato')
    customer = models.ForeignKey(
        Customer, related_name='invoices', on_delete=models.PROTECT
    )
    locked = models.BooleanField('låst', default=False)
    exported = models.BooleanField('eksportert', default=False)

    def __str__(self):
        return '%s %s' % (self.date, self.customer)

    def total(self):
        total = 0
        print('check')
        for line in self.lines.all():
            print(line)
            total += line.amount
        print(total)
        return '%skr' % intcomma(total)

    class Meta:
        verbose_name = 'faktura'
        verbose_name_plural = 'fakturaer'


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    account = models.CharField('konto', max_length=6)
    cost_center = models.CharField('ansvar', max_length=4)
    function = models.IntegerField('funksjon')
    dim3 = models.CharField('anlegg/ressurs', max_length=8, blank=True, null=True)
    dim4 = models.CharField('prosjekt', max_length=8, blank=True, null=True)
    dim5 = models.CharField('dimensjon 5', max_length=8, blank=True, null=True)
    dim6 = models.CharField('dimensjon 6', max_length=8, blank=True, null=True)
    tax = models.CharField('avgiftskode', max_length=2, default='06', blank=True)
    text = models.CharField('tekst', max_length=200)
    amount = models.DecimalField('beløp', max_digits=8, decimal_places=2)
    tax_code = models.CharField('avgiftskode', max_length=3, default='06')

    class Meta:
        verbose_name = 'fakturalinje'
        verbose_name_plural = 'fakturalinjer'
        unique_together = [
            'invoice',
            'account',
            'cost_center',
            'function',
            'text',
            'amount',
        ]

    def __str__(self):
        return 'Konto: %s Ansvar: %s Funksjon: %s Beløp: %s' % (
            self.account,
            self.cost_center,
            self.function,
            intcomma(self.amount),
        )
