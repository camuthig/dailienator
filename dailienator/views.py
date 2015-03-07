from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy


class Login(FormView):
    form_class = AuthenticationForm
    template_name = "home/login.html"

    def get(self, request, *args, **kwargs):
        if(request.user.is_authenticated()):
            return redirect('accountuser-list')
        else:
            return super(Login, self).get(self, request, *args, **kwargs)

    def form_valid(self, form):
        redirect_to = settings.LOGIN_REDIRECT_URL
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return HttpResponseRedirect(redirect_to)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(Login, self).dispatch(request, *args, **kwargs)

class Logout(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)

class PasswordUpdateView(FormView):
    template_name = 'administration/password_update.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accountuser-list')

    def get_form_kwargs(self):
        kwargs = super(PasswordUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your password has been changed.")
        return super(FormView, self).form_valid(form)
