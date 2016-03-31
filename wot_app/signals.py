from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from wot_app.tasks import task_check_event_condition
from . import models


@receiver(pre_save, sender=models.ResourceData)
def resource_data_pre_save(sender, **kwargs):
    resource_data = kwargs['instance']
    resource = resource_data.resource
    resource.validate_data(resource_data.data)


@receiver(post_save, sender=models.ResourceData)
def resource_data_post_save(sender, **kwargs):
    resource_data = kwargs['instance']
    resource = resource_data.resource
    for event in resource.events.all():
        task_check_event_condition.delay(event, resource_data)