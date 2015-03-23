import uuid
import logging

from django.views.generic import FormView
from django.contrib.messages.views import SuccessMessageMixin

from dailienator.config import settings
from dailienator.sodexoaccounts.models import AccountUser, Account

from dailienator.support.tasks import sendSupportRequest, sendSupportConfirm
from forms import SupportRequestForm

logger = logging.getLogger(__name__)

class SupportRequestView(SuccessMessageMixin, FormView):
    form_class = SupportRequestForm
    success_url = '/'
    success_message = 'An email has been sent to our support team. They will respond based on our SLA.'
    template_name = 'support/support_form.html'
    email_template_name = 'support/support_request.txt'
    confirm_template_name = 'support/confirm_request'

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            requestor_email = self.request.user.email
            request_user = self.request.user
        else:
            requestor_email = self.request.POST['email']
            user_matches = AccountUser.objects.filter(email = self.request.POST['email'])
            if len(user_matches) != 0:
                request_user = user_matches[0]

        if request_user:
            user = {
                'first_name': request_user.first_name,
                'last_name': request_user.last_name,
                'account': request_user.account.name if request_user.account else ''
            }

        # Create a large random number to identify the error
        request_number = uuid.uuid4().hex
        context = {
            'request_number': request_number,
            'user': user,
            'user_email': requestor_email,
            'issue_category': self.request.POST['issue_category'],
            'issue_description': self.request.POST['issue_description'],
            'support_page': self.request.build_absolute_uri()
        }

        sendSupportRequest.delay(self.email_template_name, context)
        sendSupportConfirm.delay(self.confirm_template_name, context)
        return super(SupportRequestView, self).form_valid(form)

    def get_form_kwargs(self):
        """
        Add the user to the post form kwargs so that validation can be done
        as to whether the user is logged in or not.
        """
        kwargs = super(SupportRequestView, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'user': self.request.user,
            })

        return kwargs