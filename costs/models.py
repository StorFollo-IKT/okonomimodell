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
    price = models.IntegerField('Pris')

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
        return Sector.objects.get(department_prefix=int(self.number/1000), customer=self.customer)


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


class Application(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='Kunde', related_name='applications')
    name = models.CharField('Applikasjonsnavn', max_length=100)
    vendor = models.CharField('Leverandør', max_length=100)
    cloud = models.BooleanField('Skytjeneste')
    servers = models.ManyToManyField(Server, verbose_name='Servere', related_name='applications', blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Ansvar')
    integrations = models.ManyToManyField('self', verbose_name='Integrasjoner', related_name='integrated', blank=True)
    licence_cost = models.IntegerField('Lisenskostnad', null=True, blank=True)
    internal_hours = models.IntegerField('Applikasjonsdrift timer pr mnd', null=True, blank=True)
    external_cost = models.IntegerField('Konsulentkostnad', null=True, blank=True)
    responsible = models.ForeignKey(User, verbose_name='Systemansvarlig', on_delete=models.PROTECT, related_name='responsible', blank=True, null=True)
    super_user = models.ForeignKey(User, verbose_name='Superbruker', on_delete=models.PROTECT, related_name='super_user', blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'applikasjon'
        verbose_name_plural = 'applikasjoner'
        unique_together = ['customer', 'name', 'department']

    def cost(self):
        cost_sum = 0
        for server in self.servers.all():
            cost_sum += server.application_cost()
        return cost_sum



    # def server_cost(self):


class Sector(models.Model):
    name = models.CharField('Navn', max_length=50)
    department_prefix = models.IntegerField('Første siffer i ansvar')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Kunde', related_name='sectors')

    def departments(self):
        return Department.objects.filter(number__gte=self.department_prefix*1000,
                                         number__lt=(self.department_prefix+1)*1000)

    def __str__(self):
        return '%s %s' % (self.customer, self.name)

    class Meta:
        verbose_name = 'Sektor'
        verbose_name_plural = 'Sektorer'
        unique_together = ['department_prefix', 'customer']
