import uuid
import logging

from django.views.generic import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import mail_admins, EmailMultiAlternatives
from django.template import loader

from dailienator.config import settings
from dailienator.sodexoaccounts.models import AccountUser, Account
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
            request_user = AccountUser.objects.filter(email = self.request.POST['email'])



        # Create a large random number to identify the error
        request_number = uuid.uuid4().hex
        context = {
            'request_number': request_number,
            'user': request_user,
            'user_email': requestor_email,
            'issue_category': self.request.POST['issue_category'],
            'issue_description': self.request.POST['issue_description'],
            'support_page': self.request.build_absolute_uri()
        }

        self.sendSupportRequest(context)
        self.sendSupportConfirm(context)
        # email = EmailMessage('Support Request ' + request_number, body, 'dailienator.py@gmail.com', [settings.EMAIL_HOST_USER])
        # email.send()
        return super(SupportRequestView, self).form_valid(form)

    def sendSupportRequest(self, context):
        logger.debug(context)
        body = loader.render_to_string(self.email_template_name,
                                       context).strip()
        mail_admins('Support Request ' + context.get('request_number'), body)

    def sendSupportConfirm(self, context):
        subject, from_email, to = 'Support Confirmation: ' + context.get('request_number'), settings.SERVER_EMAIL, context.get('user_email')
        text_content = loader.render_to_string(self.confirm_template_name + '.txt', context).strip()
        html_content = loader.render_to_string(self.confirm_template_name + '.html', context).strip()
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

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