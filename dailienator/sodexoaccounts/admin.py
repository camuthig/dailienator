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
    class Meta(UserCreationForm.Meta):
        model = AccountUser

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            AccountUser.objects.get(username=username)
        except AccountUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

class AccountUserAdmin(UserAdmin):
    form = AccountUserChangeForm
    add_form = AccountUserCreationForm

    fieldsets = UserAdmin.fieldsets + (
            ('Catertrax Information', {'fields': ('catertrax_username',
                                                    'account')}),
    )

admin.site.register(AccountUser, AccountUserAdmin)

class AccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(Account, AccountAdmin)
