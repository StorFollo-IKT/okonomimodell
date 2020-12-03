from costs.models import ProductDelivery
from invoice.build.InvoiceUtils import InvoiceUtils
from invoice.models import Invoice, InvoiceLine

account = '119520'


class BuildProductDeliveries:
    @staticmethod
    def build_lines(invoice: Invoice):
        if invoice.locked:
            print('Invoice %s is locked' % invoice)
            return
        deliveries = ProductDelivery.objects.exclude(account=None)
        deliveries = deliveries.filter(customer=invoice.customer)

        for delivery in deliveries:
            text = '%s, %d stk' % (delivery.amount, delivery.product.name)
            line = InvoiceLine(invoice=invoice,
                               account=delivery.account,
                               cost_center=delivery.cost_center.value,
                               function=delivery.function.value,
                               amount=delivery.sum(),
                               tax_code=InvoiceUtils.tax_code(invoice.customer.id, 0),
                               text=text,
                               )
            line.save()
