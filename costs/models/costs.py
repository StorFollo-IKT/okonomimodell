from django.db import models
from django.db.models import Sum
from employee_info.models import Company, CostCenter, Function

from . import Customer, User, Server, Product


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

    def sector(self):
        try:
            return self.sector_dep.get(departments__number=self.number)
        except Sector.MultipleObjectsReturned as e:
            print(e)
            print('Department %s matched multiple sectors:' % self)
            sectors = self.sector_dep.filter(departments__number=self.number)
            for sector in sectors:
                print(sector)
            return sectors.first()


class Application(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Kunde', related_name='applications')
    name = models.CharField('Applikasjonsnavn', max_length=100)
    vendor = models.CharField('Leverandør', max_length=100)
    cloud = models.BooleanField('Skytjeneste')
    servers = models.ManyToManyField(Server, verbose_name='Servere', related_name='applications', blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Ansvar')
    integrations = models.ManyToManyField('self', verbose_name='Integrasjoner', related_name='integrated', blank=True)
    licence_cost = models.IntegerField('Lisenskostnad', default=0)
    internal_hours = models.IntegerField('Applikasjonsdrift timer pr mnd', default=0)
    external_cost = models.IntegerField('Konsulentkostnad', default=0)
    responsible = models.ForeignKey(User, verbose_name='Systemansvarlig', on_delete=models.PROTECT,
                                    related_name='responsible', blank=True, null=True)
    super_user = models.ForeignKey(User, verbose_name='Superbruker', on_delete=models.PROTECT,
                                   related_name='super_user', blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'applikasjon'
        verbose_name_plural = 'applikasjoner'
        unique_together = ['customer', 'name', 'department']
        ordering = ['customer', 'name']

    def internal_hour_cost(self):
        product = Product.objects.get(name='Drift av applikasjon per time')
        return self.internal_hours * product.price

    def internal_hour_cost_year(self):
        return self.internal_hour_cost() * 12

    def server_cost(self):
        """
        Server cost per month
        :return:
        """
        server_cost = 0
        for server in self.servers.all():
            server_cost += server.application_cost()
        return server_cost

    def server_cost_year(self):
        return self.server_cost() * 12

    def external_cost_total(self):
        return self.external_cost + self.licence_cost

    def cost(self):
        return self.server_cost() + self.external_cost + self.licence_cost

    def internal_cost_total_year(self):
        return self.internal_hour_cost_year() + self.server_cost_year()

    def total_year(self):
        return self.server_cost_year() + self.external_cost_total() + self.internal_hour_cost_year()


class CostDistribution(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name='applikasjon',
                                    related_name='distributions')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='firma')
    percentage = models.IntegerField(verbose_name='prosent')

    account = models.CharField('konto', max_length=6)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.PROTECT, blank=True, null=True,
                                    verbose_name='ansvar')
    function = models.ForeignKey(Function, on_delete=models.PROTECT, verbose_name='funksjon')

    class Meta:
        unique_together = ['application', 'company', 'account', 'cost_center', 'function']

    def is_valid(self):
        lines = self.objects.filter(application=self.application)
        percent_sum = lines.aggregate(Sum('percentage'))['percentage__sum']
        return percent_sum == 100

    def customer(self):
        return self.application.customer


class Sector(models.Model):
    name = models.CharField('Navn', max_length=50)
    departments = models.ManyToManyField(Department, verbose_name='Ansvar', blank=True, related_name='sector_dep')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Kunde', related_name='sectors')

    def applications(self):
        apps = Application.objects.filter(
            department__in=self.departments.all()
        )
        return apps

    def servers(self):
        return Server.objects.filter(
            applications__department__in=self.departments.all()
        )

    def costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.cost()
        for delivery in self.deliveries.all():
            cost += delivery.sum()

        return cost

    def external_costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.external_cost

        return cost

    def licence_costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.licence_cost

        return cost

    def server_costs(self):
        apps = self.applications()
        cost = 0
        for app in apps:
            cost += app.server_cost()

        return cost

    def __str__(self):
        return '%s %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'Sektor'
        verbose_name_plural = 'Sektorer'
        unique_together = ['name', 'customer']
        ordering = ['name']


class ProductDelivery(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='Kunde', on_delete=models.PROTECT, related_name='deliveries')
    product = models.ForeignKey(Product, verbose_name='Tjeneste', on_delete=models.PROTECT, related_name='deliveries')
    amount = models.IntegerField(verbose_name='Antall')
    sector = models.ForeignKey(Sector, verbose_name='Sektor', on_delete=models.PROTECT, related_name='deliveries',
                               blank=True, null=True)

    class Meta:
        verbose_name = 'tjenesteleveranse'
        verbose_name_plural = 'tjenesteleveranser'
        unique_together = ['customer', 'product']

    def __str__(self):
        return '%s %s' % (self.customer, self.product)

    def sum(self):
        return self.product.price * self.amount

    def sum_year(self):
        return (self.product.price * self.amount) * 12


class ProductGroup(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, verbose_name='Tjenester', related_name='product_groups')

    def sum_year(self):
        total = 0
        for line in self.products.all():
            total += line.sum_year()

        return total

    class Meta:
        verbose_name = 'Tjenestegruppe'
        verbose_name_plural = 'Tjenestegrupper'
        ordering = ['name']
