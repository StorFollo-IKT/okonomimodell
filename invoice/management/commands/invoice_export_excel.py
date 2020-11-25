import datetime
import os

import xlsxwriter
from django.core.management.base import BaseCommand

from invoice.models import Invoice

now = datetime.datetime.now()
invoice_folder = '/home/datagrunnlag/Fakturaer'


class Command(BaseCommand):
    def handle(self, *args, **options):
        for invoice in Invoice.objects.filter(exported=False):
            invoice_file = os.path.join(
                invoice_folder,
                'Fordeling %s %s.xlsx'
                % (invoice.customer.name, invoice.date.strftime('%Y-%m-%d')),
            )

            # Create a workbook and add a worksheet.
            workbook = xlsxwriter.Workbook(invoice_file)
            worksheet = workbook.add_worksheet()
            row_num = 0
            for line in invoice.lines.all():
                row = [
                    line.account,
                    line.cost_center,
                    line.function,
                    line.dim3,
                    line.dim4,
                    line.dim5,
                    line.dim6,
                    line.amount,
                    line.text,
                    line.tax_code,
                ]

                worksheet.write_row(row_num, 0, row)

                row_num += 1

            workbook.close()
            print('Saved invoice to', invoice_file)
            invoice.exported = True
            invoice.locked = True
            invoice.save()
