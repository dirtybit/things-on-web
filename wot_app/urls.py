from django.conf.urls import url

from wot_app import views

urlpatterns = [
    url(r'^create-application/submit', views.application_create_submit, name='create-application-submit'),
    url(r'^create-application', views.application_create, name='create-application'),
    url(r'^create-resource/submit', views.resource_create_submit, name='create-resource-submit'),
    url(r'^create-resource', views.resource_create, name='create-resource'),
    url(r'^create-event/submit', views.event_create_submit, name='create-event-submit'),
    url(r'^create-event', views.event_create, name='create-event'),
    url(r'^$', views.homepage, name='homepage'),
    url(r'^application/([\w-]+)', views.application_detail, name='application-detail'),
    url(r'^resource/([\w-]+)', views.resource_detail, name='resource-detail'),
    url(r'^event/([\w-]+)', views.event_detail, name='event-detail'),
]