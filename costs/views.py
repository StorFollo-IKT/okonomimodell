from django.shortcuts import render, redirect

# Create your views here.
from costs.forms import ApplicationForm
from costs.models import Application, Customer, Server, Sector

from costs.utils import field_names


def customers(request):
    return render(request, 'costs/customers.html', {'customers': Customer.objects.all()})


def application_form(request):
    customer = request.GET.get('customer')
    application_name = request.GET.get('application')

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
        return redirect('costs:application', name=application_obj.name)

    context = {'form': form,
               'customers': Customer.objects.all(),
               'servers': servers,
               'application': application_obj,
               }

    return render(request, 'costs/application_form.htm', context)


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
        customer = request.GET.get('customer')

    apps = Application.objects.filter(name=name)
    if customer:
        apps = apps.filter(customer__name=customer)

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


def sectors(request):
    sectors_obj = Sector.objects.all()
    return render(request, 'costs/sectors.html',
                  {'sectors': sectors_obj})
