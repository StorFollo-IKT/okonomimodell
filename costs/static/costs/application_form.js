function select_customer(event) {
    const customer = event.target.value;
    for (input of get_server_inputs())
    {
        input.setAttribute('list', 'servers_' + customer)
    }
}

function add_field(object) {
    if (object.value === '')
        return;
    console.log(object);

    const parent = object.parentElement;
    const input_new = object.cloneNode();
    input_new.value = '';
    input_new.addEventListener("change", server_change);
    parent.appendChild(document.createElement('br'));
    parent.appendChild(input_new);
}

const customer = document.getElementById('id_customer');
customer.addEventListener("change", select_customer);


function server_change(event) {
    add_field(event.target)
}


function get_server_inputs() {
    const servers_td = document.getElementById('server_inputs');
    return servers_td.getElementsByTagName('input');
}

function get_last_server_input() {
    const inputs = get_server_inputs();
    return inputs[inputs.length - 1];
}

let input = get_last_server_input();
input.addEventListener("change", server_change);
//add_field(input);