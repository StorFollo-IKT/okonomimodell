from django import forms

from costs.models import Application, Server


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        # TODO: Rewrite user selection with AJAX autocomplete
        # <select> elements makes the load too slow
        exclude = ['responsible', 'super_user']


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        exclude = ['ad_object', 'imported']
