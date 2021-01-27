import datetime

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from employee_info.models import CostCenter, Function, Resource
from urllib.parse import urlencode

from costs.forms import ApplicationForm, CostDistributionForm, ServerForm, ProductDeliveryForm
from costs.import_utils import WorkstationsSCCM
from costs.models import Application, CostDistribution, Customer, Department, \
    Product, ProductDelivery, Sector, Server, ServerType, Workstation, User
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
    if request.user.is_authenticated:
        workstations = Workstation.objects.filter(user__email=request.user.email)
    else:
        workstations = None

    return render(request, 'costs/index.html', {'workstations': workstations})


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
        apps = sector_obj.applications
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


@permission_required('costs.view_workstation')
def workstations(request):
    workstations_obj = Workstation.objects.all()
    if request.GET.get('customer'):
        workstations_obj = workstations_obj.filter(customer__id=request.GET.get('customer'))
    has_employee = request.GET.get('has_employee')
    if has_employee == 'true':
        workstations_obj = workstations_obj.exclude(user__employee=None)
    elif has_employee == 'false':
        workstations_obj = workstations_obj.filter(user__employee=None)

    has_user = request.GET.get('has_user')
    if has_user == 'true':
        workstations_obj = workstations_obj.exclude(user=None)
    elif has_user == 'false':
        workstations_obj = workstations_obj.filter(user=None)

    return render(request, 'costs/workstations_page.html',
                  {'workstations': workstations_obj,
                   'customers': Customer.objects.exclude(workstations=None),
                   'selected_customer': request.GET.get('customer'),
                   'has_employee': has_employee,
                   'has_user': has_user,
                   'show_pus': request.user.email.find('@storfolloikt.no') > -1,
                   }
                  )


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


@permission_required('costs.delete_costdistribution')
def cost_distribution_delete(request):
    distribution_id = request.GET.get('id')
    distribution = CostDistribution.objects.get(id=distribution_id)
    distribution.delete()
    return HttpResponseRedirect(reverse('costs:cost_distribution') + '?application=%s' % distribution.application_id)


@permission_required('costs.show_product')
def licenses(request):
    products = Product.objects.filter(type__type='Lisens')
    product_arg = request.GET.get('product')
    if request.GET.get('user'):
        products = products.filter(user__id=request.GET.get('user'))
    if product_arg:
        users = User.objects.filter(products__name=product_arg)
        return render(request, 'costs/licenses_user.html', {'users': users, 'title': product_arg})

    customer_licenses = {}
    customers_with_licences = []
    for product in products:
        for customer in Customer.objects.all():
            if customer not in customer_licenses:
                customer_licenses[customer] = {}

            product_users = product.users.filter(customer=customer)
            if product_users and customer not in customers_with_licences:
                customers_with_licences.append(customer)
            customer_licenses[customer][product] = product_users

    return render(request, 'costs/licenses.html', {'title': 'Lisenser', 'products': products,
                                                   'customer_licences': customer_licenses,
                                                   'customers': customers_with_licences})


@csrf_exempt
def import_sccm(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Request method must be POST')
    customer = Customer.objects.get(id=request.GET.get('customer'))
    load = WorkstationsSCCM(customer)
    load.save_file(request.body)
    return HttpResponse('OK')


@permission_required('costs.show_customer')
def customer_company(request):
    customer = request.GET.get('customer')
    customer_obj = get_object_or_404(Customer, id=customer)
    return HttpResponse(customer_obj.company.companyCode)


@permission_required('costs.change_productdelivery')
def product_delivery(request):
    delivery_id = request.GET.get('id')
    if delivery_id:
        delivery_obj = ProductDelivery.objects.get(id=delivery_id)
    else:
        delivery_obj = None

    form = ProductDeliveryForm(request.POST or None, instance=delivery_obj)
    if request.method == 'POST':
        fields = request.POST.dict()
        print(fields)

        if fields['cost_center']:
            cost_center_obj = CostCenter.objects.get(company__customer__id=form.data['customer'],
                                                     value=form.data['cost_center'])
            fields['cost_center'] = cost_center_obj.id

        if fields['function']:
            function_obj = Function.objects.get(company__customer__id=form.data['customer'],
                                                value=form.data['function'])
            fields['function'] = function_obj.id

        print(fields)
        form = ProductDeliveryForm(fields, instance=delivery_obj)

        if form.is_valid():
            delivery_obj = form.save()
        # return redirect('costs:portfolio')

    return render(request, 'costs/product_delivery_form.html', {'form': form,
                                                                'delivery': delivery_obj})


@permission_required('costs.show_product')
def products(request):
    products_obj = Product.objects.all()
    return render(request, 'costs/products.html', {'products': products_obj})


@permission_required('costs.show_user')
def product_users(request):
    value = request.GET.get('product')
    product_obj = Product.objects.get(name=value)
    return render(request, 'costs/users.html', {'users': product_obj.users.all()})


@permission_required('costs.show_user')
def user(request):
    user_id = request.GET.get('id')
    user_obj = User.objects.get(id=user_id)
    return render(request, 'costs/user.html', {
        'user': user_obj,
        'title': 'Bruker %s' % user_obj.name,
        'show_pus': request.user.email.find('@storfolloikt.no') > -1
    })
