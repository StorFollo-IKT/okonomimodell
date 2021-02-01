I views.py:
Hent GET parametere:

    application_name = request.GET.get('application')
    server_type = request.GET.get('type')
    product = request.GET.get('product')
    active = request.GET.get('active')

Legg til i context:

	'customers': filter_list('name', model=Customer),
	'types': filter_list('type', model=ServerType),
	'products': filter_list('name', queryset=products),


Legg til head:

    <link rel="stylesheet" href="{% static 'costs/filter.css' %}" type="text/css">
    <script type="application/javascript" src="{% static 'costs/filter.js' %}"></script>
	
Legg til div:

        <div id="filter">
            <h2>Filtrering</h2>
        </div>

Legg til data:

    {{ customers|json_script:'customer-data' }}
    {{ types|json_script:'type-data' }}
    {{ products|json_script:'product-data' }}


    <script>
      const filter_group = new filterGroup('filter')
      filter_group.addFilterJson('customer', 'Etter kunde')
      filter_group.addFilterJson('type', 'Etter type')
      filter_group.addFilterJson('product', 'Etter tjeneste')
    </script>
	
