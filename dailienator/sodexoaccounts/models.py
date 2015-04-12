from django.db import models

from django.contrib.auth.models import AbstractUser
from dailienator.common.aesfield.field import AESField
from dailienator.common.utils.model_helper import unique_slugify

# Create your models here.

class AccountUser(AbstractUser):
    catertrax_username = models.CharField(max_length=255, blank=True)
    catertrax_password = AESField(max_length=255, blank=True, aes_key='catertrax_key')
    account = models.ForeignKey('Account', null=True)

    def __unicode__(self):
        return self.username

class Account(models.Model):
    name = models.CharField(max_length=50, blank=False)
    catertrax_url = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, blank=True)
    header_slogan = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name

class AccountStaticDailyEntry(models.Model):
    column_choices = (
        ('guest_count', 'Guest Count'),
        ('set_time', 'Set Time'),
        ('contract_number', 'Contract Number'),
        ('location', 'Location'),
        ('service_style', 'Service Style'),
        ('pick_up_time', 'Pick Up Time'),
        ('assigned_caterer', 'Assigned Caterer'),
        ('special_instructions', 'Special Instructions'),
        ('lead_on_event', 'Lead On Event'),
        ('vehicle_col', 'Vehicle'),
    )
    position_choices = (
        ('start', 'Start'),
        ('end', 'End'),
    )
    # start or end
    position = models.CharField(max_length=50, blank=False, choices=position_choices)
    # the name of the columns leveraged in dailygenerator
    column   = models.CharField(max_length=50, blank=False, choices=column_choices)
    value    = models.CharField(max_length=255, blank=True)
    account  = models.ForeignKey('Account', null=False)

    class Meta:
        unique_together = ('position', 'column', 'account')

    def __unicode__(self):
        return self.position + '|' + self.column + '|' + self.value

    def human_readable_column(self):
        """
            Break up the column to have spaces and capital letters
            instead of snake case.
        """
        parts = self.column.split('_')
        readable = ' '.join(parts)
        return readable.title()

    def human_readable_position(self):
        """
            Give our position a title casing
        """
        return self.position.title()