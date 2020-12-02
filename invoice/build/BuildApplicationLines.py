from costs.models import Application
from invoice.build.InvoiceUtils import InvoiceUtils
from invoice.models import InvoiceLine, Invoice


class BuildApplicationLines:
    def build_lines(self, invoice: Invoice):
        if invoice.locked:
            print('Invoice %s is locked' % invoice)
            return
        for app in invoice.customer.applications.all():
            self.application_line(invoice, app)

    @staticmethod
    def application_line(invoice: Invoice, app: Application, debug=False):
        if app.distributions.count() > 0:
            if not app.total_year():
                print('%s has no cost' % app)
                return
            if not app.distribution_valid():
                print('Distribution for %s is not valid' % app)
                return

            if debug:
                print(app)
            for distribution in app.distributions.all():
                if debug:
                    print(
                        '%s%% of %skr = %skr'
                        % (
                            distribution.percentage,
                            distribution.application.total_year(),
                            distribution.amount(),
                        )
                    )

                text = '%s' % app.name

                line = InvoiceLine(
                    invoice=invoice,
                    text=text,
                    account=distribution.account,
                    cost_center=distribution.cost_center.value,
                    function=distribution.function.value,
                    amount=(distribution.amount() / 12) * 1.25,
                    tax_code=InvoiceUtils.tax_code(invoice.customer.id, 25),
                )
                if debug:
                    print(line)
                line.save()
