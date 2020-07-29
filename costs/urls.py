from django.urls import path

from . import views

app_name = 'costs'

urlpatterns = [
    path('', views.applications, name='applications'),
    path('applikasjon_form', views.application_form, name='application_form'),

    path('applikasjon/<str:customer>/<str:name>', views.application, name='application'),
    path('applikasjon/<str:name>', views.application, name='application'),
    path('server/form', views.server_form, name='server_form'),
    path('server/<str:customer>/<str:name>', views.server_detail, name='server'),
    path('servere', views.servers_all, name='servers'),
    path('servere/<str:customer>', views.servers_all, name='servers'),
    path('kunder', views.customers, name='customers'),
    path('portefolje', views.portfolio, name='portfolio'),
    path('applikasjoner', views.applications, name='applications'),
    path('applikasjoner/kunde/<str:customer>', views.applications, name='applications'),
    path('applikasjoner/kunde/<str:customer>/<str:department>', views.applications, name='applications'),
    path('applikasjoner/kunde/<str:customer>/sektor/<int:sector>', views.applications, name='applications'),
    path('applikasjoner/leverandor/<str:vendor>', views.applications, name='applications'),
    path('sectors', views.sectors, name='sectors'),
    path('ansvar', views.departments, name='departments'),
    path('accounts/profile/', views.applications)
]
