from django.db import models


class ProductType(models.Model):
    type = models.CharField('Tjenestetype', max_length=50)
    description = models.TextField('Beskrivelse', null=True, blank=True)

    class Meta:
        verbose_name = 'tjenestetype'
        verbose_name_plural = 'tjenestetyper'

    def __str__(self):
        return self.type


class Product(models.Model):
    name = models.CharField('Tjeneste', max_length=50)
    type = models.ForeignKey(ProductType, on_delete=models.PROTECT, verbose_name='Tjenestetype')
    price = models.IntegerField('Pris per måned')

    class Meta:
        verbose_name = 'tjeneste'
        verbose_name_plural = 'tjenester'

    def __str__(self):
        return '%s: %s' % (self.type, self.name)

    def user_count(self):
        return self.users.count()
