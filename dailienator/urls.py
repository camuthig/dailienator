from django.conf.urls import patterns, include, url
from sodexoaccounts.views import AccountUserListView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dailienator.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    #Home
    url(r'^$', 'dailienator.sodexoaccounts.views.home',),
    
    #Daily AccountUser Views
    url(r'^users/$', AccountUserListView.as_view(), name='accountuser-list'),
    
)
