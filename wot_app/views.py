import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.template.context import Context, RequestContext
from oauth2_provider.models import AccessToken, RefreshToken
from oauth2_provider.settings import oauth2_settings
from datetime import datetime, timedelta
from oauthlib.common import generate_token

from wot_app.models import Application, Resource, Event


@login_required
def application_create(request, *args, **kwargs):
    return render(request, 'create-application.html')


@login_required
def application_create_submit(request, *args, **kwargs):
    print(request.POST)
    app_name = request.POST.get('appName')
    is_private = request.POST.get('isPrivate', False)

    succeeded = False
    token = None
    api_url = None

    if app_name:
        token = generate_token()
        scopes = oauth2_settings.SCOPES
        user = User.objects.first()
        application = Application.objects.create(authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
                                                 client_type=Application.CLIENT_PUBLIC,
                                                 redirect_uris='http://localhost:8000',
                                                 name=app_name,
                                                 is_private=is_private,
                                                 user=user)
        access_token = AccessToken.objects.create(
                user=user,
                application=application,
                token=token,
                expires=datetime.now() + timedelta(days=365),
                scope=scopes)

        RefreshToken.objects.create(
                user=user,
                token=generate_token(),
                access_token=access_token,
                application=application)
        succeeded = True
        api_url = application.url

    return render(request, 'create-application-submit.html', context=Context({'succeeded': succeeded,
                                                                              'token': token,
                                                                              'api_url': api_url}))


@login_required
def resource_create(request, *args, **kwargs):
    token = request.GET.get('token')
    return render(request, 'create-resource.html', context=RequestContext(request, {'token': token}))


@login_required
def resource_create_submit(request, *args, **kwargs):
    token = request.POST.get('token')
    res_name = request.POST.get('name', False)
    data_fields = json.loads(request.POST.get('data-fields', False))

    try:
        access_token = AccessToken.objects.get(token=token)
    except:
        return render(request, 'create-resource-submit.html', context=Context({'succeeded': False,
                                                                               'error': 'Invalid token'}))

    application = access_token.application
    resource = Resource.objects.create(application=application, name=res_name, data_fields=data_fields)
    res_url = resource.url

    return render(request, 'create-resource-submit.html', context=Context({'succeeded': True,
                                                                           'res_url': res_url}))

@login_required
def event_create(request, *args, **kwargs):
    token = request.GET.get('token')
    resource = request.GET.get('res')
    return render(request, 'create-event.html', context=RequestContext(request, {'token': token,
                                                                                 'resource': resource}))


@login_required
def event_create_submit(request, *args, **kwargs):
    print(request.POST)
    token = request.POST.get('token')
    ev_name = request.POST.get('name', False)
    res_name = request.POST.get('resource', False)
    condition = json.loads(request.POST.get('condition', False))

    try:
        access_token = AccessToken.objects.get(token=token)
    except:
        return render(request, 'create-event-submit.html', context=Context({'succeeded': False,
                                                                            'error': 'Invalid token'}))

    try:
        resource = Resource.objects.get(slug=res_name)
    except:
        return render(request, 'create-event-submit.html', context=Context({'succeeded': False,
                                                                            'error': 'Invalid resource name'}))

    application = access_token.application
    event = Event.objects.create(resource=resource, application=application, condition=condition, name=ev_name)
    ev_url = event.url

    return render(request, 'create-event-submit.html', context=Context({'succeeded': True,
                                                                        'ev_url': ev_url}))


@login_required
def homepage(request, *args, **kwargs):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'homepage.html', context=Context({'applications': applications}))


@login_required
def application_detail(request, app_slug, *args, **kwargs):
    application = get_object_or_404(Application, slug=app_slug)
    return render(request, 'application-detail.html', context=Context({'application': application,
                                                                       'token': application.accesstoken_set.last(),
                                                                       'resources': application.resources.all()}))


@login_required
def resource_detail(request, res_slug, *args, **kwargs):
    resource = get_object_or_404(Resource, slug=res_slug)
    application = resource.application
    return render(request, 'resource-detail.html', context=Context({'resource': resource,
                                                                    'token': application.accesstoken_set.last(),
                                                                    'events': resource.events.all()}))


@login_required
def event_detail(request, ev_slug, *args, **kwargs):
    event = get_object_or_404(Event, slug=ev_slug)
    return render(request, 'event-detail.html', context=Context({'event': event,
                                                                 'subscribers': event.subscriptions.all()}))