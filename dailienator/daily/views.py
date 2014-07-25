from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages

from dailienator.sodexoaccounts.models import AccountUser, Account

from forms import DailyCreateForm
from dailygenerator import DailyGenerator

class DailyCreateView(FormView):
    template_name = 'daily_create_form.html'
    form_class = DailyCreateForm
    success_url = reverse_lazy('daily-create')

    def form_valid(self, request, *args, **kwargs):
        date = self.request.POST.get('date')
        print date
        generator = DailyGenerator()
        try:
            print 'before the result' 
            result = generator.generateDaily(account_user, date)
            print 'after the result'
            #messages.success(request, 'Successfully created daily for ' + str(date))
        except Exception as e:
            pass
            #messages.error(request, "An error occurred generating the daily."+
            #    " If this continues, please contact dailienator.py@gmail.com "+
            #    "for support.")
        return HttpResponseRedirect(self.get_success_url())
