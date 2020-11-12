from costs.models import Application
from invoice.models import InvoiceLine, Invoice


class BuildApplicationLines:
    def build_lines(self, invoice: Invoice):
        if invoice.locked:
            print('Invoice %s is locked' % invoice)
            return
        for app in invoice.customer.applications.all():
            self.application_line(invoice, app)

    @staticmethod
    def application_line(invoice: Invoice, app: Application):
        if app.distributions.count() > 0:
            if not app.cost():
                print('%s has no cost' % app)
                return
            if not app.distribution_valid():
                print('Distribution for %s is not valid' % app)
                return

            print(app)
            for distribution in app.distributions.all():
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
                )
                print(line)
                line.save()
