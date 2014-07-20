from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from dailienator.sodexoaccounts.models import AccountUser, Account

class AccountUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        widgets = {'catertrax_password': forms.PasswordInput(),}

class AccountUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        widgets = {'catertrax_password': forms.PasswordInput(),}

class AccountUserAdmin(UserAdmin):
    form = AccountUserChangeForm
    add_form = AccountUserCreationForm
    
    fieldsets = UserAdmin.fieldsets + (
            ('Catertrax Information', {'fields': ('catertrax_username',
            										'catertrax_password')}),
    )

admin.site.register(AccountUser, AccountUserAdmin)

class AccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(Account, AccountAdmin)