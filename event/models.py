from django.db import models
from django.conf import settings

class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft' , 'Draft'
        PUBLISHED = 'published' , 'Published'
        FINISHED = 'finished' , 'Finished'
        CANCELLED = 'calncelled' , 'Cancelled'

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image = models.ImageField(upload_to='events/',null=True,blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,)

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='attended_events',
        blank=True
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class EventAttribute(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EventAttributeValue(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attribute_values',
    )
    attribute = models.ForeignKey(
        EventAttribute,
        on_delete=models.CASCADE,
    )
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ('event','attribute')

    def __str__(self):
        return f"{self.event.title} - {self.attribute.name} : {self.value}"