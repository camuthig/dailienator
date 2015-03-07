from django.conf.urls import patterns, include, url
from sodexoaccounts.views import AccountUserListView, AccountUserCreateView, AccountUserUpdateView, AccountUserDeleteView, AccountUpdateView, AccountUserCaterTraxPasswordUpdateView
from views import Login, Logout, PasswordUpdateView
from daily.views import DailyCreateView

from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from django.contrib.auth.views import password_change
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dailienator.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    #Home
    url(r'^$', Login.as_view(), name='login'),
    url(r'^logout$', Logout.as_view(), name='logout'),

    #Sodexo AccountUser Views
    url(r'^users/$', AccountUserListView.as_view(), name='accountuser-list'),
    url(r'^users/create$', AccountUserCreateView.as_view(), name='accountuser-create'),
    url(r'^users/password/update$', PasswordUpdateView.as_view(), name='password-update'),
    url(r'^users/catertrax_password/update', AccountUserCaterTraxPasswordUpdateView.as_view(), name='accountuser-catertrax-password-update'),
    url(r'^users/(?P<username>[\w|.|@|+|-]+)/update', AccountUserUpdateView.as_view(), name='accountuser-update'),
    url(r'^users/(?P<username>[\w|.|@|+|-]+)/delete', AccountUserDeleteView.as_view(), name='accountuser-delete'),

    #Sodexo Account Views
    url(r'^account/update', AccountUpdateView.as_view(), name='account-update'),

    #Daily Views
    url(r'^daily/create$', DailyCreateView.as_view(), name='daily-create'),
)
