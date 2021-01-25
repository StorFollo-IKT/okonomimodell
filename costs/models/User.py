from django.db import models
from employee_info.models import CostCenter, Resource

from ad_import.models import User as ADUser
from . import Customer, Product, Student


class User(models.Model):
    number = models.IntegerField('Ressursnummer', null=True)
    ad_user = models.CharField('Brukernavn AD', max_length=50)
    ad_object = models.OneToOneField(ADUser, on_delete=models.CASCADE, null=True, default=None, verbose_name='AD',
                                     related_name='users')
    name = models.CharField('Navn', max_length=100, null=True)
    employee = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name='ansatt', null=True, default=None)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='elev', null=True, default=None)
    email = models.EmailField('Epostadresse', null=True)
    dn = models.CharField('DN', max_length=300, blank=True, null=True)
    customer = models.ForeignKey(Customer, related_name='users', on_delete=models.PROTECT, verbose_name='Kunde', null=True, default=None)
    products = models.ManyToManyField(Product, related_name='users', verbose_name='tjenester', blank=True)

    class Meta:
        verbose_name = 'bruker'
        verbose_name_plural = 'brukere'
        ordering = ['name']

    def company(self):
        if self.employee:
            return self.employee.company

    def department(self) -> CostCenter:
        if self.employee:
            main_position = self.employee.main_position()
            if main_position:
                return main_position.costCenter

    def last_logon(self):
        if self.ad_object:
            return self.ad_object.lastLogon

    def last_update(self):
        if self.ad_object:
            return self.ad_object.last_update

    def has_ad(self):
        return self.ad_object is not None

    def has_product(self, product):
        return product in self.products.all()

    def display_name(self):
        return self.ad_object.displayName

    def username(self):
        return self.ad_object.sAMAccountName

    def __str__(self):
        return '%s (%s)' % (self.name, self.customer)
