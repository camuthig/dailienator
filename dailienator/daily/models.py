from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class AccountUser(AbstractUser):
    catertrax_username = models.CharField(max_length=255, blank=False)
    catertrax_password = models.CharField(max_length=255, blank=False)
