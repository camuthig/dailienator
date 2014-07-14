from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import logging
from models import AccountUser
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

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

class AccountUserCreateView(CreateView):
    model = AccountUser
    fields = ['username', 'first_name', 'last_name', 'email',
    			'catertrax_username']

class AccountUserUpdateView(UpdateView):
    model = AccountUser
    fields = ['username', 'first_name', 'last_name', 'email',
    			'catertrax_username']

class AccountUserDeleteView(DeleteView):
    model = AccountUser
    success_url = reverse_lazy('accountuser-list') 
