from django import template
from django.db.models import QuerySet

from costs.models import Customer

register = template.Library()


@register.filter
def filter_customer(products: QuerySet, customer: Customer):
    return products.filter(customer=customer).count()
