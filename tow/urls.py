from django.conf.urls import include, url
from django.contrib import admin
from wot_app.api.urls import urlpatterns as wot_api_urls
from wot_app.urls import urlpatterns as wot_ui_urls

from wot_app.api.views import notification_endpoint

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^api/', include(wot_api_urls)),
    url(r'^hook', notification_endpoint),
    url(r'^', include(wot_ui_urls)),
]
