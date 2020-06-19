from django.db import models


class Customer(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField('Navn', max_length=50)
    served_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Driftes av')

    class Meta:
        verbose_name = 'kunde'
        verbose_name_plural = 'kunder'

    def __str__(self):
        return self.name

    def costs(self):
        cost = 0
        for application in self.applications.all():
            cost += application.cost()
        for product in self.deliveries.all():
            cost += product.sum()

        return cost


class ProductType(models.Model):
    type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'tjenestetype'
        verbose_name_plural = 'tjenestetyper'

    def __str__(self):
        return self.type


class Product(models.Model):
    name = models.CharField('Tjeneste', max_length=50)
    type = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    price = models.IntegerField('Pris per måned')

    class Meta:
        verbose_name = 'tjeneste'
        verbose_name_plural = 'tjenester'

    def __str__(self):
        return '%s: %s' % (self.type, self.name)


class Server(models.Model):
    name = models.CharField('Navn', max_length=50)
    dns_name = models.CharField('DNS-navn', max_length=100, null=True, blank=True)
    dn = models.CharField('DN', max_length=200)
    description = models.CharField('Beskrivelse', max_length=100, null=True, blank=True)
    last_logon = models.DateTimeField('Sist aktiv', null=True, blank=True)
    last_update = models.DateTimeField('Sist oppdatert', auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='servers', verbose_name='Tjeneste', null=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Kunde', related_name='servers')

    class Meta:
        unique_together = ['name', 'customer']
        verbose_name = 'server'
        verbose_name_plural = 'servere'

    def __str__(self):
        value = '%s: %s' % (self.customer, self.name)
        if self.product:
            value += ' (%s)' % self.product
        return value

    def applications_string(self):
        apps_string = ''
        for app in self.applications.all():
            apps_string += str(app) + "\n"

        return apps_string

    def application_cost(self):
        if not self.product or not self.product.price:
            return 0
        return round(self.product.price/self.applications.count())


class Department(models.Model):
    number = models.IntegerField('Ansvar')
    name = models.CharField('Navn', max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

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


class User(models.Model):
    number = models.IntegerField('Ressursnummer')
    ad_user = models.CharField('Brukernavn AD', max_length=50)
    name = models.CharField('Navn', max_length=100)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    email = models.EmailField('Epostadresse')

    class Meta:
        unique_together = ['number', 'ad_user', 'department']
        verbose_name = 'bruker'
        verbose_name_plural = 'brukere'
        ordering = ['name']

    def customer(self):
        """
        Shortcut method used in admin
        :return: Customer
        """
        return self.department.customer


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
    responsible = models.ForeignKey(User, verbose_name='Systemansvarlig', on_delete=models.PROTECT, related_name='responsible', blank=True, null=True)
    super_user = models.ForeignKey(User, verbose_name='Superbruker', on_delete=models.PROTECT, related_name='super_user', blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'applikasjon'
        verbose_name_plural = 'applikasjoner'
        unique_together = ['customer', 'name', 'department']
        ordering = ['customer', 'name']

    def server_cost(self):
        server_cost = 0
        for server in self.servers.all():
            server_cost += server.application_cost()
        return server_cost

    def cost(self):
        return self.server_cost() + self.external_cost + self.licence_cost


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
    sector = models.ForeignKey(Sector, verbose_name='Sektor', on_delete=models.PROTECT, related_name='deliveries', blank=True, null=True)

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
