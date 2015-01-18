from django import forms
from django.contrib.auth.forms import UserCreationForm

from models import AccountUser

class AccountUserCreateForm(forms.ModelForm):
    password2 = forms.CharField(label="Confirm Password",
                                    widget=forms.PasswordInput,
                                    required=True,)
    password1 = forms.CharField(label="Password",
                                    widget=forms.PasswordInput,
                                    required=True)

    confirm_ct_password = forms.CharField(label="Confirm Catertrax Password",
                                            widget=forms.PasswordInput,
                                            required=True,)
    catertrax_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = AccountUser
        fields = ['username', 'password1', 'password2', 'first_name',
                'last_name', 'email','catertrax_username', 'catertrax_password',
                'confirm_ct_password']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AccountUserCreateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AccountUserCreateForm, self).clean()
        ct_password1 = cleaned_data.get("catertrax_password")
        ct_password2 = cleaned_data.get("confirm_ct_password")

        if (ct_password1 and ct_password2 and ct_password1 != ct_password2):
            raise forms.ValidationError("Catertrax passwords did not match.")
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(AccountUserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        #Set the account ID to be that of the requesting user's.
        user.account = self.user.account
        if commit:
            user.save()
        return user

class AccountUserCaterTraxPasswordUpdateForm(forms.ModelForm):
    confirm_ct_password = forms.CharField(label="Confirm Catertrax Password",
                                            widget=forms.PasswordInput,
                                            required=True,)
    catertrax_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = AccountUser
        fields = ['catertrax_password', 'confirm_ct_password']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AccountUserCaterTraxPasswordUpdateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AccountUserCaterTraxPasswordUpdateForm, self).clean()
        ct_password1 = cleaned_data.get("catertrax_password")
        ct_password2 = cleaned_data.get("confirm_ct_password")

        if (ct_password1 and ct_password2 and ct_password1 != ct_password2):
            raise forms.ValidationError("Catertrax passwords did not match.")
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = super(AccountUserCaterTraxPasswordUpdateForm, self).clean()
        self.user.catertrax_password = cleaned_data.get("catertrax_password")
        self.user.save()
        return self.user

