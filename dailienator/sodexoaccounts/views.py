from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist

from django.http import Http404

import logging

from dailienator.common.utils.mixins import LoginRequiredMixin
from models import AccountUser, Account
from forms import AccountUserCreateForm, AccountUserCaterTraxPasswordUpdateForm, AccountUserUpdateForm

# Create your views here.

logger = logging.getLogger(__name__)

class AccountUserListView(LoginRequiredMixin, ListView):
    model = AccountUser
    fields = ['username', 'first_name', 'last_name']
    paginate_by = 15

    def get_queryset(self):
        return AccountUser.objects.filter(account = self.request.user.account)

class AccountUserCreateView(LoginRequiredMixin, CreateView):
    model = AccountUser
    form_class = AccountUserCreateForm
    template_name = "sodexoaccounts/accountuser_create_form.html"
    success_url=reverse_lazy('accountuser-list')

    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(AccountUserCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class AccountUserUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountUser
    form_class = AccountUserUpdateForm
    template_name = "sodexoaccounts/accountuser_update_form.html"

    def get_success_url(self):
        return reverse_lazy('accountuser-update', kwargs=self.kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        param_username = self.kwargs.get('username')

        if param_username is not None:
            queryset = queryset.filter(username=param_username)
        else:
            raise AttributeError("{0}: AccountUser update view must be called with username.".format(
                                    self.__class__.__name__))
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

class AccountUserCaterTraxPasswordUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountUser
    form_class = AccountUserCaterTraxPasswordUpdateForm
    template_name = "sodexoaccounts/catertrax_password_update.html"

    def get_queryset(self):
        return AccountUser.objects.filter(account = self.request.user.account)
    def get_success_url(self):
        self.kwargs['username'] = self.request.user.username
        return reverse_lazy('accountuser-update', kwargs=self.kwargs)
    def get_object(self, queryset=None):
        return self.request.user.account
    def get_form_kwargs(self):
        # pass "user" keyword argument with the current user to your form
        kwargs = super(AccountUserCaterTraxPasswordUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class AccountUserDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountUser
    success_url = reverse_lazy('accountuser-list')

    def get_queryset(self):
        return AccountUser.objects.filter(account = self.request.user.account)
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        param_username = self.kwargs.get('username')

        if param_username is not None:
            queryset = queryset.filter(username=param_username)
        else:
            raise AttributeError("{0}: AccountUser delete view must be called with username.".format(
                                    self.__class__.__name__))
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    template_name = "sodexoaccounts/account_update_form.html"
    fields = ['name', 'catertrax_url']
    def get_success_url(self):
        return reverse_lazy('account-update')

    def get_object(self, queryset=None):
        account = self.request.user.account
        if account is not None:
            return account
        else:
            raise Http404("{0}: Account update requires an account user in the request.".format(
                                    self.__class__.__name__))
