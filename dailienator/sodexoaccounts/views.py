from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist

from django.http import Http404

import logging

from models import AccountUser
from forms import AccountUserCreateForm

# Create your views here.

logger = logging.getLogger(__name__)

#this was login_user, but I'm just testing
def home(request):
    if request.method == 'POST':
        messages.set_level(request, messages.ERROR)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                print ('Successfully logged in.')
                logger.debug('Logged in successfully, redirecting to home page.')
                return redirect('/users/')
            else:
                messages.error(request, 'The given user is inactive.')
                return render(request, "home/login.html")
                # Return a 'disabled account' error message
        else:
            messages.error(request, 'Invalid username/password')
            return render(request, "home/login.html") 
    else:
        return render(request, "home/login.html")

class AccountUserListView(ListView):
    model = AccountUser
    fields = ['username', 'first_name', 'last_name']
    paginate_by = 15

class AccountUserCreateView(CreateView):
    model = AccountUser
    form_class = AccountUserCreateForm
    success_url=reverse_lazy('accountuser-list')

class AccountUserUpdateView(UpdateView):
    model = AccountUser
    fields = ['username', 'first_name', 'last_name', 'email',
    			'catertrax_username']
    def get_success_url(self):
        return reverse_lazy('accountuser-update', kwargs=self.kwargs)
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        param_username = self.kwargs.get('username')

        if param_username is not None:
            queryset = queryset.filter(username=param_username)
        else:
            raise AttributeError("AccountUser delete view must be called with username."
                                    % self.__class__.__name__)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

class AccountUserDeleteView(DeleteView):
    model = AccountUser
    success_url = reverse_lazy('accountuser-list') 
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        param_username = self.kwargs.get('username')

        if param_username is not None:
            queryset = queryset.filter(username=param_username)
        else:
            raise AttributeError("AccountUser delete view must be called with username."
                                    % self.__class__.__name__)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
