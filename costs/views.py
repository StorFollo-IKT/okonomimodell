from django.shortcuts import render

# Create your views here.
from costs.forms import ApplicationForm
from costs.models import Application, Customer, Server, Sector


def customers(request):
    return render(request, 'costs/customers.html', {'customers': Customer.objects.all()})


def application_form(request):
    customer = request.GET.get('customer')
    application_name = request.GET.get('application')

    if customer and application_name:
        application_obj = Application.objects.get(name=application_name, customer__id=customer)
    else:
        application_obj = None

    form = ApplicationForm(request.POST or None, instance=application_obj)

    return render(request, 'costs/application_form.htm', {'form': form, 'customers': Customer.objects.all()})


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
        apps = apps.filter(department__number__gte=sector*1000, department__number__lt=(sector+1)*1000)

    if server:
        apps = apps.filter(servers__name=server)
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


def application(request, name, customer=None):
    if not customer:
        customer = request.GET.get('customer', '')

    apps = Application.objects.filter(name=name)
    if customer:
        apps = apps.filter(customer__name=customer)

    apps_sorted = {}

    for app in apps:
        apps_sorted[app.customer.name] = app
    apps = apps.order_by('customer')
    return render(request, 'costs/application.html', {'applications': apps, 'title': name,
                                                      })


def server_detail(request, name, customer):
    server = Server.objects.get(name=name, customer__name=customer)
    return render(request, 'costs/server.html', {'server': server,
                                                 'title': '%s: %s' % (server.customer, server.name)})


def servers_all(request, customer=None):
    if not customer:
        customer = request.GET.get('customer', '')
    application_name = request.GET.get('application')

    custs = Customer.objects.all()
    servers = Server.objects.all()
    if customer:
        custs = custs.filter(name=customer)
        servers = servers.filter(customer__name=customer)
    if application_name:
        servers.filter(applications__name=application_name)
    return render(request, 'costs/servers.html', {'customers': custs, 'servers': servers})
