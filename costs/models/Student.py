from django.db import models

from costs.models import Customer


class Student(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    firstName = models.CharField('fornavn', max_length=200)
    lastName = models.CharField('etternavn', max_length=200)
    ssn = models.CharField('fødselsnummer', max_length=11)
    guid = models.CharField('GUID', max_length=36)

    def __str__(self):
        return self.firstName + ' ' + self.lastName
