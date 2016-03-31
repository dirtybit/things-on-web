import json
import logging

from autoslug.fields import AutoSlugField
from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.
from django.db.models.fields import CharField, BooleanField
from django.db.models.fields.related import ForeignKey
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField
from oauth2_provider.models import AbstractApplication

from wot_app.exceptions import InvalidResourceDataException

logger = logging.getLogger(__name__)


class Application(AbstractApplication, TimeStampedModel):

    is_private = BooleanField(default=False)
    slug = AutoSlugField(populate_from='name', unique=True)

    @cached_property
    def url(self):
        return reverse('application', kwargs={'app_slug': self.slug})

    @cached_property
    def to_dict(self):
        events = [dict(name=ev.slug, url=ev.url) for ev in self.events.all()]
        resources = [dict(name=res.slug, url=res.url) for res in self.resources.all()]
        return {
            "name": self.slug,
            "url": self.url,
            "modified": self.modified,
            "created": self.created,
            "data": {
                "events": events,
                "resource": resources
            }
        }


class Resource(TimeStampedModel):

    name = CharField(max_length=100)
    data_fields = JSONField()
    application = ForeignKey(Application, related_name='resources')
    slug = AutoSlugField(populate_from='name', unique=True)

    def validate_data(self, resource_data):
        extra_fields = set(resource_data.keys()).difference(self.data_fields.keys())
        if extra_fields:
            raise InvalidResourceDataException

        for k, val in resource_data.items():
            expected_type = self.data_fields[k]
            if type(val).__name__ != expected_type:
                if expected_type == 'float':
                    try:
                        float(val)
                    except ValueError:
                        raise InvalidResourceDataException
                else:
                    raise InvalidResourceDataException

    @cached_property
    def url(self):
        return reverse('resource', kwargs={'app_slug': self.application.slug,
                                           'res_slug': self.slug})

    @cached_property
    def to_dict(self):
        return {
            "url": self.url,
            "modified": self.modified,
            "created": self.created,
            "data": {
                "name": self.slug,
                "data_fields": self.data_fields,
                "application": {
                    "name": self.application.slug,
                    "url": self.application.url
                }
            }
        }


class ResourceData(TimeStampedModel):

    resource = ForeignKey(Resource, on_delete=models.DO_NOTHING, related_name='all_data')
    data = JSONField()


class Event(TimeStampedModel):

    name = CharField(max_length=100)
    condition = JSONField()
    resource = ForeignKey(Resource, on_delete=models.DO_NOTHING, related_name='events')
    application = ForeignKey(Application, related_name='events')
    slug = AutoSlugField(populate_from='name', unique=True)

    def check_condition(self, resource_data):
        import operator
        data = resource_data.data
        cond = self.condition
        try:
            return all(getattr(operator, opstr)(data[field], value) for field, opstr, value in cond)
        except:
            logger.exception('Error occurred while checking event condition')

    @cached_property
    def url(self):
        return reverse('event', kwargs={'app_slug': self.application.slug,
                                        'res_slug': self.resource.slug,
                                        'ev_slug': self.slug})

    @cached_property
    def to_dict(self):
        return {
            "url": self.url,
            "modified": self.modified,
            "created": self.created,
            "data": {
                "resource": {
                    "name": self.resource.slug,
                    "url": self.resource.url
                },
                "application": {
                    "name": self.application.slug,
                    "url": self.application.url
                },
                "name": self.slug,
                "condition": self.condition
            }
        }


class EventSubscription(TimeStampedModel):

    event = ForeignKey(Event, on_delete=models.DO_NOTHING, related_name='subscriptions')
    notify_url = CharField(max_length=255)

    @cached_property
    def url(self):
        return reverse('subscription', kwargs={'app_slug': self.event.application.slug,
                                               'res_slug': self.event.resource.slug,
                                               'ev_slug': self.event.slug,
                                               'subs_id': self.id})

    @cached_property
    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "modified": self.modified,
            "created": self.created,
            "data": {
                "event": {
                    "name": self.event.slug,
                    "url": self.event.url
                },
                "resource": {
                    "name": self.event.resource.slug,
                    "url": self.event.resource.url
                },
                "application": {
                    "name": self.event.application.slug,
                    "url": self.event.application.url
                },
                "notify_url": self.notify_url
            }
        }
