from django.http.response import HttpResponse
from oauth2_provider.models import AccessToken
from wot_app.decorators import filter_paths
from wot_app.models import Application
import logging

logger = logging.getLogger(__name__)


@filter_paths(include=['/api/'])
class OauthApplicationMiddleware:

    def process_view(self, request, view_callback, view_args, view_kwargs):
        app_slug = view_kwargs.get('app_slug')
        try:
            app = Application.objects.get(slug=app_slug)
            request.application = app
            logger.info("OauthApplicationMiddleware: %s(%s) -- %s", app.name, app.id, request.path)
            return None
        except Exception:
            logger.exception("OauthApplicationMiddleware: Error occured for app %s -- %s", app_slug, request.path)
            return HttpResponse(status=400)


class OauthAccessTokenMiddleware:

    def process_request(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            request.access_token = AccessToken.objects.get(token=token)
        except Exception:
            request.access_token = None
