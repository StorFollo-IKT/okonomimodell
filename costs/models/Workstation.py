from django.db import models

from ad_import.models import (
    Workstation as ADWorkstation,
    User as ADUser,
    Directory,
)
from employee_info.models import CostCenter, Function
from . import Customer, User, Product


class Workstation(models.Model):
    name = models.CharField('navn', max_length=100, blank=True, null=True)
    distinguishedName = models.CharField('DN', max_length=300, blank=True, null=True)
    ad_object = models.OneToOneField(
        ADWorkstation,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        verbose_name='AD',
        related_name='workstation',
    )
    manufacturer = models.CharField('merke', max_length=100, blank=True, null=True)
    model = models.CharField('modell', max_length=100, blank=True, null=True)
    serial = models.CharField(
        'serienummer', max_length=100, blank=True, null=True, unique=True
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name='kunde',
        null=True,
        default=None,
        related_name='workstations',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='siste bruker',
        null=True,
        default=None,
        related_name='workstations_user',
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='eier',
        null=True,
        default=None,
        related_name='workstations',
    )
    user_name = models.CharField('brukernavn', max_length=100, blank=True, null=True)
    user_domain = models.CharField(
        'brukerdomene', max_length=100, blank=True, null=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='tjeneste',
        null=True,
        default=None,
        related_name='workstations',
    )

    leased = models.BooleanField('leid', default=False)
    last_logon = models.DateTimeField('Siste pålogging', blank=True, null=True)
    pus_id = models.IntegerField('PureService ID', blank=True, null=True)

    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.PROTECT,
        verbose_name='ansvar',
        null=True,
        default=None,
        related_name='workstations',
    )

    function = models.ForeignKey(
        Function,
        on_delete=models.PROTECT,
        verbose_name='funksjon',
        null=True,
        default=None,
        related_name='workstations',
    )

    class Meta:
        verbose_name = 'arbeidsstasjon'
        verbose_name_plural = 'arbeidsstasjoner'
        ordering = ['customer', 'model']

    def __str__(self):
        return self.name

    def ad_computer_lookup(self) -> ADWorkstation:
        return ADWorkstation.objects.get(distinguishedName=self.distinguishedName)

    def ad_user_lookup(self, directory: Directory) -> ADUser:
        return ADUser.objects.get(
            sAMAccountName__iexact=self.user_name, directory=directory
        )

    def user_lookup(self, directory: Directory):
        ad_user = self.ad_user_lookup(directory)
        return User.objects.get(ad_object=ad_user)

    def user_display_name(self):
        if self.user:
            return self.user.display_name()
        else:
            return '%s\\%s' % (self.user_domain, self.user_name)

    def owner_display_name(self):
        if self.owner:
            return self.owner.display_name()
