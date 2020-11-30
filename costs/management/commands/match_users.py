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
            if not user.customer:
                print('%s has no customer' % user)
                continue

            if not user.ad_object:
                print('%s has no AD object' % user)
                continue

            if not user.ad_object.employeeID:
                if user.ad_object.employeeNumber:
                    try:
                        employee = Resource.objects.get(company=user.customer.company,
                                                        socialSecurityNumber=user.ad_object.employeeNumber)
                        user.employee = employee
                        user.save()
                    except Resource.DoesNotExist:
                        print('No resource in company %s with SSN %s' % (user.customer.company,
                                                                         user.ad_object.employeeNumber))

            else:
                try:
                    resource_id = int(user.ad_object.employeeID)
                except ValueError:
                    print('Invalid resource ID for %s: %s' % (user, user.ad_object.employeeID))
                    continue

                try:
                    employee = Resource.objects.get(company=user.customer.company,
                                                    resourceId=resource_id)
                    user.employee = employee
                    user.save()
                except Resource.DoesNotExist:
                    print('No resource in company %s with resourceId %s' % (user.customer.company, resource_id))
