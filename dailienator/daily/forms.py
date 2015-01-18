from django import forms
from bootstrap3_datetime.widgets import DateTimePicker

class DailyCreateForm(forms.Form):
    date = forms.DateField(
        widget=DateTimePicker(options={"format": "MM/DD/YYYY",
                                       "pickTime": False}))