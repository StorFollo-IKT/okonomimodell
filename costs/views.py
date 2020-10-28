import datetime

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from employee_info.models import CostCenter, Function, Resource
from urllib.parse import urlencode

from costs.forms import ApplicationForm, CostDistributionForm, ServerForm
from costs.models import Application, CostDistribution, Customer, Department, Product, ProductDelivery, Sector, Server, \
    ServerType
from costs.utils import field_names, filter_list


def build_title(word, vendor=None, sector=None, server=None, customer=None):
    title = word
    if vendor:
        title += ' levert av %s' % vendor
    if sector:
        title += ' i sektor %s' % sector
    if server:
        title += ' på server %s' % server
    if customer:
        title += ' hos %s' % customer

    return title


def index(request):
    return render(request, 'costs/index.html')


@permission_required('costs.view_customer')
def customers(request):
    return render(request, 'costs/customers.html', {'customers': Customer.objects.all()})


@permission_required('costs.add_application')
def application_form(request):
    customer = request.GET.get('customer')
    application_name = request.GET.get('name')

    if customer and application_name:
        application_obj = Application.objects.get(name=application_name, customer__id=customer)
        servers = application_obj.servers.all()
    else:
        application_obj = None
        servers = None

    form = ApplicationForm(request.POST or None, instance=application_obj)
    if request.method == 'POST' and form.is_valid():
        application_obj = form.save()
        servers = request.POST.getlist('servers_list')

        for server in servers:
            if server == '':
                continue
            application_obj.servers.add(Server.objects.get(name=server))

        query = {'name': application_obj.name}
        if application_obj.customer:
            query['customer'] = application_obj.customer
        query = urlencode(query)
        url = reverse('costs:application') + '?' + query
        return HttpResponseRedirect(url)

    context = {'form': form,
               'customers': Customer.objects.all(),
               'servers': servers,
               'application': application_obj,
               }

    return render(request, 'costs/application_form.htm', context)


@permission_required('costs.change_server')
def server_form(request):
    customer = request.GET.get('customer')
    server_name = request.GET.get('server')
    if customer and server_name:
        server_obj = Server.objects.get(name=server_name, customer__id=customer)
    else:
        server_obj = None

    form = ServerForm(request.POST or None, instance=server_obj)
    if request.method == 'POST' and form.is_valid():
        server_obj = form.save()
        return redirect('costs:server', customer=server_obj.customer.name, name=server_obj.name)

    return render(request, 'costs/server_form.html', {'form': form})


@permission_required('costs.view_application')
def applications(request, customer=None, vendor=None, department=None, sector=None):
    apps = Application.objects.all()
    title = Application._meta.verbose_name_plural
    sectors = None

    if not customer:
        customer = request.GET.get('customer')
    if not vendor:
        vendor = request.GET.get('vendor')
    if not department:
        department = request.GET.get('department')
    if not sector:
        sector = request.GET.get('sector')
    server = request.GET.get('server')

    if customer and department:
        apps = apps.filter(customer__name=customer, department__number=department)
        selected_customer = customer
    elif customer:
        apps = apps.filter(customer__name=customer)
        sectors = Sector.objects.filter(customer__name=customer)
        title += ' hos %s' % customer
        selected_customer = customer
    if vendor:
        apps = apps.filter(vendor=vendor)
        title += ' levert av %s' % vendor

    if sector:
        sector_obj = Sector.objects.get(customer__name=customer,
                                        name=sector)
        apps = sector_obj.applications()
        title += ' i sektor %s' % sector

    if server:
        apps = Application.objects.filter(servers__name=server, servers__customer__name=customer)
        title += ' på server %s' % server

    apps = apps.order_by('name')
    return render(request, 'costs/applications.htm', {'applications': apps,
                                                      'title': title,
                                                      'customers': Customer.objects.all(),
                                                      'sectors': sectors,
                                                      'selected_customer': customer,
                                                      'selected_department': department,
                                                      'selected_vendor': vendor,
                                                      'selected_sector': sector})


@permission_required('costs.view_application')
def application(request, name=None, customer=None):
    if not name:
        name = request.GET.get('name')
    if not customer:
        customer = request.GET.get('customer')

    apps = Application.objects.filter(name=name)
    if customer:
        apps = apps.filter(customer__id=customer)

    apps_sorted = {}

    for app in apps:
        apps_sorted[app.customer.name] = app
    apps = apps.order_by('customer')
    return render(request, 'costs/application.html', {
        'applications': apps,
        'application_name': name,
        'title': name,
        'customer': customer,
        'fields': field_names(Application._meta)
    })


@permission_required('costs.view_server')
def server_detail(request, name, customer):
    server = Server.objects.get(name=name, customer__name=customer)
    return render(request, 'costs/server.html', {'server': server,
                                                 'title': '%s: %s' % (server.customer, server.name)})


@permission_required('costs.view_server')
def servers_all(request, customer=None):
    if not customer:
        customer = request.GET.get('customer', '')
    application_name = request.GET.get('application')
    server_type = request.GET.get('type')
    product = request.GET.get('product')
    active = request.GET.get('active')

    servers = Server.objects.all()
    if customer:
        servers = servers.filter(customer__name=customer)

    title = build_title('Servere', customer=customer)

    if application_name:
        servers = servers.filter(applications__name=application_name)
        title += ' for applikasjon %s' % application_name
    if active:
        days = int(active)
        limit_date = datetime.datetime.today() - datetime.timedelta(days=days)
        servers = servers.filter(last_logon__gte=limit_date)
        title += ' aktive siste %d dager' % days

    if server_type:
        servers = servers.filter(type__type=server_type)

    if product:
        servers = servers.filter(product__name=product)

    products = Product.objects.filter(type__type='Server')
    return render(request, 'costs/servers.html',
                  {'customers': filter_list('name', model=Customer),
                   'types': filter_list('type', model=ServerType),
                   'products': filter_list('name', queryset=products),
                   'servers': servers,
                   'title': title,
                   'selected_customer': customer,
                   'selected_product': product})


@permission_required('costs.view_sector')
def sectors(request):
    sector = request.GET.get('sector')
    if not sector:
        sectors_obj = Sector.objects.order_by('name').values_list('name').distinct()
        costs = {}
        for sector_name in sectors_obj:
            sector_name = sector_name[0]
            costs[sector_name] = 0

            for sector in Sector.objects.filter(name=sector_name):
                costs[sector_name] += sector.costs()

        return render(request, 'costs/sectors_all.html',
                      {'sectors': costs.items()})
    else:
        sectors_obj = Sector.objects.filter(name=sector)
        return render(request, 'costs/sector.html',
                      {'sectors': sectors_obj})


@permission_required('costs.view_application')
def portfolio(request):
    applications_obj = Application.objects.all()
    deliveries_obj = ProductDelivery.objects.all()
    customer = request.GET.get('customer', 'all')
    sector = request.GET.get('sector', 'all')
    application_name = request.GET.get('application', 'all')
    title = ''
    if customer and customer != 'all':
        applications_obj = applications_obj.filter(customer__name=customer)
        deliveries_obj = deliveries_obj.filter(customer__name=customer)
        title += ' hos %s' % customer

    if sector and sector != 'all':
        applications_obj = applications_obj.filter(department__sector_dep__name=sector)
        deliveries_obj = deliveries_obj.filter(sector__name=sector)
        title += ' i sektor %s' % sector

    vendor = request.GET.get('vendor', 'all')
    if vendor and vendor != 'all':
        applications_obj = applications_obj.filter(vendor=vendor)

    if application_name and application_name != 'all':
        applications_obj = applications_obj.filter(name=application_name)

    # applications_unique = Application.objects.order_by('name').values_list('name', flat=True).distinct()
    applications_unique = applications_obj.order_by('name').values_list('name', flat=True).distinct()
    sectors_unique = Sector.objects.order_by('name').values_list('name', flat=True).distinct()
    vendors_unique = applications_obj.order_by('vendor').values_list('vendor', flat=True).distinct()

    return render(request, 'costs/portfolio.html',
                  {'applications': applications_obj,
                   'deliveries': deliveries_obj,
                   'applications_unique': applications_unique,
                   'customers': Customer.objects.all(),
                   'sectors': sectors_unique,
                   'vendors': vendors_unique,
                   'selected_application': application_name,
                   'selected_customer': customer,
                   'selected_vendor': vendor,
                   'selected_sector': sector
                   })


@permission_required('costs.view_department')
def departments(request):
    return render(request, 'costs/departments.html',
                  {'departments': Department.objects.all()})


@permission_required('costs.view_application')
def report(request):
    common_apps = Application.objects.filter(department=None)
    department_apps = Application.objects.all()
    department_apps = department_apps.exclude(department=None)
    deliveries = ProductDelivery.objects.all()

    customer = request.GET.get('customer')

    if customer:
        common_apps = common_apps.filter(customer__name=customer)
        department_apps = department_apps.filter(customer__name=customer)
        deliveries = deliveries.filter(customer__name=customer)

    # common_apps_cost_sum = common_apps.aggregate(Sum('licence_cost'))
    # common_apps_cost_sum += common_apps.aggregate(Sum('external_cost'))

    sector = request.GET.get('sector')
    if sector:
        department_apps = department_apps.filter(department__sector_dep__name=sector)

    department = request.GET.get('department')
    if department:
        department_apps = department_apps.filter(department__name=department)

    sector_names = Sector.objects.all().distinct()

    return render(request, 'costs/cost_report.html',
                  {'common_apps': common_apps,
                   'department_apps': department_apps,
                   'customers': filter_list('name', model=Customer),
                   'sectors': filter_list('name', queryset=sector_names),
                   'deliveries': deliveries,
                   'customer': customer,
                   'sector': sector,
                   }
                  )


@permission_required('costs.change_costdistribution')
def cost_distribution(request):
    application_id = request.GET.get('application')
    app = Application.objects.get(id=application_id)
    distributions = CostDistribution.objects.filter(application=app)
    errors = ''
    if request.method == 'POST':
        for field in request.POST.keys():
            if 'distribution' not in field:
                continue

            row = request.POST.getlist(field)
            try:
                if len(row) == 5:
                    distribution_obj = CostDistribution.objects.get(id=row[4], application=app)
                else:
                    distribution_obj = CostDistribution(application=app)

                cost_center = CostCenter.objects.get(company=app.customer.company, value=row[1])
                function = Function.objects.get(company=app.customer.company, value=row[2])
            except ObjectDoesNotExist:
                continue

            form = CostDistributionForm({'account': row[0],
                                         'cost_center': cost_center,
                                         'function': function,
                                         'percentage': row[3]}, instance=distribution_obj)
            if form.is_valid():
                try:
                    form.save()
                except IntegrityError as e:
                    errors = str(e)
            else:
                errors = form.errors

    title = 'Fordel kostnader for %s hos %s' % (app.name, app.customer)

    return render(request, 'costs/cost_distribution.html', {'title': title,
                                                            'distributions': distributions,
                                                            'application': app,
                                                            'errors': errors})
