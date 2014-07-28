from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
import logging
import traceback

from dailienator.sodexoaccounts.models import AccountUser, Account

from forms import DailyCreateForm
from dailygenerator import DailyGenerator

logger = logging.getLogger(__name__)

class DailyCreateView(FormView):
    template_name = 'daily_create_form.html'
    form_class = DailyCreateForm
    success_url = reverse_lazy('daily-create')

    def form_valid(self, request, *args, **kwargs):
        date = self.request.POST.get('date')
        account_user = self.request.user
        generator = DailyGenerator()
        try:
            logger.info('Creating daily as ' + account_user.username +
                ' for date ' + date)
            result = generator.generateDaily(account_user, date)
            logger.info('Finished creating daily as ' + account_user.username +
                ' for date ' + date)
            #messages.success(request, 'Successfully created daily for ' + str(date))
        except Exception as e:
            logger.error('Error handling request to create daily from ' + account_user.username +
                ' for date ' + date)
            logger.error(traceback.format_exc())
            #messages.error(request, "An error occurred generating the daily."+
            #    " If this continues, please contact dailienator.py@gmail.com "+
            #    "for support.")
        return HttpResponseRedirect(self.get_success_url())
