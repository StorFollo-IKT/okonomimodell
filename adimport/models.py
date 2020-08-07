from django.db import models

from costs.models import Application, Customer, User, Product


class Directory(models.Model):
    dn = models.CharField(max_length=100)
    dc = models.GenericIPAddressField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    ldaps = models.BooleanField(default=False)

    def __str__(self):
        return self.dn


IMPORT_TARGETS = [('adimport.Workstation', 'Workstation'),
                  ('costs.Server', 'Server'),
                  ('costs.User', 'User'),
                  ('adimport.Group', 'Group')]


class Query(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    directory = models.ForeignKey(Directory, on_delete=models.PROTECT)
    query = models.CharField(max_length=200)
    base_dn = models.CharField('Base DN', max_length=200, blank=True, null=True)
    type = models.CharField(max_length=15, choices=[('user', 'User'), ('computer', 'Computer'), ('group', 'Group')])
    target = models.CharField(max_length=200, choices=IMPORT_TARGETS)

    def __str__(self):
        return '%s %s' % (self.directory.dn, self.query)

    class Meta:
        verbose_name = 'LDAP query'
        verbose_name_plural = 'LDAP queries'


class Group(models.Model):
    directory = models.ForeignKey(Directory, on_delete=models.PROTECT)
    name = models.CharField(max_length=200, null=True, blank=True)
    dn = models.CharField(max_length=200)
    members = models.ManyToManyField(User, blank=True)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)

    def check_customer(self):
        if self.directory.customer != self.application.customer:
            return False
        else:
            return True


class Workstation(models.Model):
    name = models.CharField('Navn', max_length=50)
    dns_name = models.CharField('DNS-navn', max_length=100, null=True, blank=True)
    dn = models.CharField('DN', max_length=200, null=True, blank=True)
    description = models.CharField('Beskrivelse', max_length=100, null=True, blank=True)
    last_logon = models.DateTimeField('Sist aktiv', null=True, blank=True)
    last_update = models.DateTimeField('Sist oppdatert', auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='workstations', verbose_name='Tjeneste',
                                null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Kunde', related_name='workstations')
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = ['name', 'customer']
        verbose_name = 'arbeidsstasjon'
        verbose_name_plural = 'arbeidsstasjoner'
        ordering = ['customer', 'name']

    def __str__(self):
        value = '%s: %s' % (self.customer, self.name)
        if self.product:
            value += ' (%s)' % self.product
        return value
