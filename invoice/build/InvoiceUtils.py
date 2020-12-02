import datetime

from costs.models import Customer
from invoice.models import Invoice


class InvoiceUtils:
    @staticmethod
    def tax_code(company, percent=25):
        if company == 'AK':
            if percent == 0:
                return '0'
            elif percent == 25:
                return '06'
            else:
                raise AttributeError('Invalid tax amount')
        elif company == 'FK':
            if percent == 0:
                return '0'
            elif percent == 25:
                return '2A'
            elif percent == 15:
                return '2B'
            elif percent == 12:
                return '2C'
            else:
                raise AttributeError('Invalid tax amount')

    @staticmethod
    def get_latest_invoice(customer_obj: Customer):
        today = datetime.date.today()
        try:
            return Invoice.objects.get(
                customer=customer_obj, date__year=today.year, date__month=today.month
            )
        except Invoice.DoesNotExist:
            print(
                'No invoice created for %s %s-%s'
                % (customer_obj, today.year, today.month)
            )
            return
