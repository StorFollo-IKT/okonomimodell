function footerCallback(row, data, start, end, display) {
    var api = this.api(), data;
    // Remove the formatting to get integer data for summation

    api.columns('.sum', {page: 'current'}).every(function () {
        var sum = this
            .data()
            .reduce(function (a, b) {
                return intVal(a) + intVal(b);
            }, 0);

        this.footer().innerHTML = sum.toLocaleString().replace(/,/g, ' ') + ' kr';
    });

}

function intVal(i) {
    return typeof i === 'string' ?
        i.replace(/\D/g, '') * 1 :
        typeof i === 'number' ?
            i : 0;
};

function calculateYearlyTotal() {
    var sum = 0;
    $('.yearlyTotal').each(function () {
        sum += intVal($(this).text());
    });
    $('#totalSum').text(sum.toLocaleString().replace(/,/g, ' ') + ' kr');
}