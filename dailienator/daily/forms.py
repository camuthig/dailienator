from functools import partial
from django import forms

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class DailyCreateForm(forms.Form):
    date = forms.DateField(widget=DateInput())