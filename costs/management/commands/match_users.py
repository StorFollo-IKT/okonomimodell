"""
Match users from AD to Resources
"""
import datetime
from django.core.management.base import BaseCommand
from employee_info.models import Resource

from costs.models import User

now = datetime.datetime.now()


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all():
            company = user.customer().id
            try:
                employee = Resource.objects.get(company__companyCode=company,
                                                resourceId=user.number)
                user.employee = employee
                user.save()
            except Resource.DoesNotExist:
                print('No resource in company %s with resourceId %s' % (company, user.number))
