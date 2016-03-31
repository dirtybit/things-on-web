import json
import logging

from braces.views import JsonRequestResponseMixin, CsrfExemptMixin
from django import http
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from oauth2_provider.views.generic import ProtectedResourceMixin

from wot_app.exceptions import InvalidResourceDataException
from wot_app.models import Application, Resource, Event, ResourceData, EventSubscription

logger = logging.getLogger(__name__)


class ProtectedResourceApiMixin(ProtectedResourceMixin):
    def dispatch(self, request, *args, **kwargs):
        if (
            request.application.is_private and
            request.application != request.access_token.application
        ):
            return HttpResponseForbidden()
        else:
            return super().dispatch(request, *args, **kwargs)


class ResourceApiBaseView(View):
    def _fetch_resource_objects(self, view_kwargs):
        app_slug = view_kwargs.get('app_slug')
        self.application = get_object_or_404(Application, slug=app_slug)

    def dispatch(self, request, *args, **kwargs):
        self._fetch_resource_objects(kwargs)

        if self.application is None:
            logger.warning('Application not found from slug')
            return http.HttpResponseBadRequest()

        return super().dispatch(request, *args, **kwargs)


class ProtectedRestApiView(ProtectedResourceApiMixin, JsonRequestResponseMixin, ResourceApiBaseView):
    from oauth2_provider.settings import oauth2_settings

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS


class ResourceApiView(CsrfExemptMixin, ProtectedRestApiView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.resource = None
        res_slug = kwargs.get('res_slug')
        if res_slug:
            self.resource = get_object_or_404(Resource, slug=res_slug)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logger.info('ResourceApiView.get called')

        if self.resource:
            resource_data = self.resource.all_data.order_by('id').last()
            if resource_data:
                data = {'data': resource_data.data, 'time': resource_data.created}
            else:
                data = {}
        else:
            data = [res.to_dict for res in self.application.resources.all()]

        return self.render_json_response(data)

    def post(self, request, *args, **kwargs):
        if self.resource:
            return self._write_resource_data()
        else:
            return self._create_resource()

    def _write_resource_data(self):
        data = self.request_json
        try:
            ResourceData.objects.create(data=data, resource=self.resource)
            return HttpResponse(status=200)
        except InvalidResourceDataException:
            logger.exception('Resource data does not conform to specified structure')
            return HttpResponseBadRequest()

    def _create_resource(self):
        data = self.request_json
        kwargs = {'application': self.application}
        kwargs.update(data)
        try:
            resource = Resource.objects.create(**kwargs)
            response = HttpResponse(status=201)
            response['Location'] = resource.url
            return response
        except:
            logger.exception('Create resource failed -- payload:\n%s', data)
            return HttpResponseBadRequest()


class EventApiView(CsrfExemptMixin, ProtectedRestApiView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.resource = None
        res_slug = kwargs.get('res_slug')
        if res_slug:
            self.resource = get_object_or_404(Resource, slug=res_slug)

        self.event = None
        ev_slug = kwargs.get('ev_slug')
        if ev_slug:
            self.event = get_object_or_404(Event, slug=ev_slug)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logger.info('EventApiView.get called')
        if self.event:
            data = self.event.to_dict
        else:
            data = [ev.to_dict for ev in self.resource.events.all()]
        return self.render_json_response(data)

    def post(self, request, *args, **kwargs):
        if self.event:
            return self.http_method_not_allowed(request, *args, **kwargs)

        data = self.request_json
        kwargs = {'application': self.application, 'resource': self.resource}
        kwargs.update(data)
        try:
            event = Event.objects.create(**kwargs)
            response = HttpResponse(status=201)
            response['Location'] = event.url
            return response
        except:
            logger.exception('Create event failed -- payload:\n%s', data)
            return HttpResponseBadRequest()

    def put(self, request, *args, **kwargs):
        if self.event is None:
            return self.http_method_not_allowed(request, *args, **kwargs)

        data = self.request_json
        try:
            Event.objects.filter(pk=self.event.pk).update(**data)
            return HttpResponse(status=200)
        except:
            logger.exception('Update event failed -- payload:\n%s', data)
            return HttpResponseBadRequest()


class EventSubscriptionApiView(ProtectedRestApiView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.subscription = None
        self.event = None
        ev_slug = kwargs.get('ev_slug')
        if ev_slug:
            self.event = get_object_or_404(Event, slug=ev_slug)

        subs_id = kwargs.get('subs_id')
        if subs_id:
            self.subscription = get_object_or_404(EventSubscription, id=subs_id)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logger.info('EventApiView.get called')
        if self.subscription:
            data = self.subscription.to_dict
        else:
            data = [subs.to_dict for subs in self.event.subscriptions.all()]
        return self.render_json_response(data)

    def post(self, request, *args, **kwargs):
        if not self.event or self.subscription:
            return self.http_method_not_allowed(request, *args, **kwargs)

        data = self.request_json
        kwargs = {'event': self.event}
        kwargs.update(data)
        try:
            subscription = EventSubscription.objects.create(**kwargs)
            response = HttpResponse(status=201)
            response['Location'] = subscription.url
            return response
        except:
            logger.exception('Create event subscription failed -- payload:\n%s', data)
            return HttpResponseBadRequest()

    def put(self, request, *args, **kwargs):
        if self.subscription is None:
            return self.http_method_not_allowed(request, *args, **kwargs)

        data = self.request_json
        try:
            EventSubscription.objects.filter(pk=self.subscription.pk).update(**data)
            return HttpResponse(status=200)
        except:
            logger.exception('Update event subscription failed -- payload:\n%s', data)
            return HttpResponseBadRequest()

    def delete(self, request, *args, **kwargs):
        if self.subscription is None:
            return self.http_method_not_allowed(request, *args, **kwargs)

        try:
            self.subscription.delete()
            return HttpResponse(status=200)
        except:
            logger.exception('Delete event subscription failed -- subs-id:\n%s', self.subscription.id)
            return HttpResponseBadRequest()


class ApplicationApi(JsonRequestResponseMixin, View):

    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, slug=kwargs.get('app_slug'))
        return self.render_json_response(application.to_dict)


@csrf_exempt
def notification_endpoint(request, *args, **kwargs):
    try:
        logger.warning('Notification received')
        logger.warning(request.body.decode())
    except:
        logger.exception('Notification handler failed')

    return HttpResponse(status=200)