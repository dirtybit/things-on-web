from django.conf.urls import url

from wot_app.api import views

"""
Endpoints

Application API:
/<app-slug>
    - GET: Get all info about the application

Resources API:
/<app-slug>/resources
    - POST: Create a resource for the app
    - GET: List all resources of the app

/<app-slug>/resources/<res-slug>
    - POST: Post the latest state of the resource
    - GET: Read the latest state of the resource

Events API:
/<app-slug>/resources/<res-slug>/events
    - POST: Create an event for the resource
    - GET: List all events of the resoure

/<app-slug>/resources/<res-slug>/events/<ev-slug>
    - PUT: Update event definition
    - GET: Read the details of the event

Event Subscription API:
/<app-slug>/resources/<res-slug>/events/<ev-slug>/subscriptions
    - POST: Subscribe to the event notification
    - GET: List all subscriptions

/<app-slug>/resources/<res-slug>/events/<ev-slug>/subscriptions/<subs-id>
    - PUT: Update event subscription
    - GET: Read the details of the event subscription
    - DELETE: Unsubcribe from the event notifications


"""

urlpatterns = [
    url(r'^(?P<app_slug>[\w-]+)/$', views.ApplicationApi.as_view(), name='application'),
    url(r'^(?P<app_slug>[\w-]+)/resources/(?P<res_slug>[\w-]+)/events/(?P<ev_slug>[\w-]+)/subscriptions/(?P<subs_id>\d+)/$',
        views.EventSubscriptionApiView.as_view(), name='subscription'),
    url(r'^(?P<app_slug>[\w-]+)/resources/(?P<res_slug>[\w-]+)/events/(?P<ev_slug>[\w-]+)/subscriptions/$',
        views.EventSubscriptionApiView.as_view(), name='subscription-list'),
    url(r'^(?P<app_slug>[\w-]+)/resources/(?P<res_slug>[\w-]+)/events/(?P<ev_slug>[\w-]+)/',
        views.EventApiView.as_view(), name='event'),
    url(r'^(?P<app_slug>[\w-]+)/resources/(?P<res_slug>[\w-]+)/events/$', views.EventApiView.as_view(), name='event-list'),
    url(r'^(?P<app_slug>[\w-]+)/resources/(?P<res_slug>[\w-]+)/', views.ResourceApiView.as_view(), name='resource'),
    url(r'^(?P<app_slug>[\w-]+)/resources/$', views.ResourceApiView.as_view(), name='resource-list'),
]