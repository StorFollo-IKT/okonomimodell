        $("#id_customer").change(function () {
            let customer = $(this).val()
            console.log(customer)
            $.get("{% url 'costs:customer_company' %}?customer=" + customer, function (company) {
                console.log(company);
                $("#id_cost_center").autocomplete({
                    source: "{% url 'employee_info_autocomplete:autocomplete_cost_center' %}?company=" + company
                });
                $("#id_function").autocomplete({
                    source: "{% url 'employee_info_autocomplete:autocomplete_function' %}?company=" + company
                });
            });
        })