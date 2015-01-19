from django.db import models

from django.contrib.auth.models import AbstractUser
from dailienator.common.aesfield.field import AESField
from dailienator.common.utils.model_helper import unique_slugify

# Create your models here.

class AccountUser(AbstractUser):
    catertrax_username = models.CharField(max_length=255, null=True, blank=False)
    catertrax_password = AESField(max_length=255, null=True, blank=False, aes_key='catertrax_key')
    account = models.ForeignKey('Account', null=True)

    def __unicode__(self):
        return self.username

class Account(models.Model):
    name = models.CharField(max_length=50, blank=False)
    catertrax_url = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, blank=True)

    def save(self, **kwargs):
        slug = '%s' % (self.name)
        unique_slugify(self, slug)
        super(Account, self).save()

    def __unicode__(self):
        return self.name
