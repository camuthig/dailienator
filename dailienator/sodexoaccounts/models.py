from django.db import models

from django.contrib.auth.models import AbstractUser
from dailienator.common.aesfield.field import AESField

# Create your models here.

class AccountUser(AbstractUser):
    catertrax_username = models.CharField(max_length=255, blank=False)
    catertrax_password = AESField(max_length=255, blank=False, aes_key='catertrax_key')
