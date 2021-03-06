from django import forms

from costs.models import Application, CostDistribution, Server, ProductDelivery


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        # TODO: Rewrite user selection with AJAX autocomplete
        # <select> elements makes the load too slow
        exclude = ['responsible', 'super_user']


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        exclude = ['ad_object', 'imported', 'last_update', 'last_logon']


class CostDistributionForm(forms.ModelForm):
    class Meta:
        model = CostDistribution
        exclude = ['application', 'company']


class ProductDeliveryForm(forms.ModelForm):
    class Meta:
        model = ProductDelivery
        exclude = ['sector'] # , 'cost_center', 'function'
        widgets = {
            'cost_center': forms.TextInput(),
            'function': forms.TextInput(),
        }
