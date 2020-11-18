from django.db import models

from ad_import.models import (
    Workstation as ADWorkstation,
    User as ADUser,
    Directory,
)
from . import Customer, User


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
        on_delete=models.PROTECT,
        verbose_name='bruker',
        null=True,
        default=None,
        related_name='workstations',
    )
    user_name = models.CharField('brukernavn', max_length=100, blank=True, null=True)
    user_domain = models.CharField(
        'brukerdomene', max_length=100, blank=True, null=True
    )

    class Meta:
        verbose_name = 'arbeidsstasjon'
        verbose_name_plural = 'arbeidsstasjoner'
        ordering = ['customer', 'model']

    def ad_computer_lookup(self) -> ADWorkstation:
        return ADWorkstation.objects.get(distinguishedName=self.distinguishedName)

    def ad_user_lookup(self, directory: Directory) -> ADUser:
        return ADUser.objects.get(
            sAMAccountName__iexact=self.user_name, directory=directory
        )

    def user_lookup(self, directory=None):
        ad_user = self.ad_user_lookup(directory)
        return User.objects.get(ad_object=ad_user)

    def user_display_name(self):
        if self.user:
            return self.user.display_name()
        else:
            return '%s\\%s' % (self.user_domain, self.user_name)