import json
import logging
import time

import requests

from tow.celery import app

logger = logging.getLogger(__name__)


@app.task
def task_notify_event_subscriber(event, subscription, resource_data):
    event_data = {
        'name': event.slug,
        'application': event.application.slug,
        'resource': {
            'name': event.resource.slug,
            'data': resource_data.data,
        }
    }
    logger.warning('Notify URL: {}'.format(subscription.notify_url))
    logger.warning('Event data: {}'.format(json.dumps(event_data)))

    try:
        requests.post(subscription.notify_url, json=event_data)
    except:
        logger.exception('Event notification failed')


@app.task
def task_check_event_condition(event, resource_data):
    if not event.check_condition(resource_data):
        return

    for subs in event.subscriptions.all():
        task_notify_event_subscriber.delay(event, subs, resource_data)
        time.sleep(1)
