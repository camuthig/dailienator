from __future__ import absolute_import

from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import loader

from django.conf import settings

@shared_task
def sendSupportRequest(email_template_name, context):
    body = loader.render_to_string(email_template_name,
                                   context).strip()
    send_mail(
        'Support Request ' + context.get('request_number'),
        body,
        settings.SERVER_EMAIL,
        settings.SUPPORTERS)

@shared_task
def sendSupportConfirm(confirm_template_name, context):
    subject, from_email, to = 'Support Confirmation: ' + context.get('request_number'), settings.SERVER_EMAIL, context.get('user_email')
    text_content = loader.render_to_string(confirm_template_name + '.txt', context).strip()
    html_content = loader.render_to_string(confirm_template_name + '.html', context).strip()
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()