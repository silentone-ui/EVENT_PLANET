from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        CLOSED = 'closed', 'Closed'
        FINISHED = 'finished', 'Finished'

    ALLOWED_TRANSITIONS = {
        Status.DRAFT: [Status.PUBLISHED],
        Status.PUBLISHED: [Status.CLOSED],
        Status.CLOSED: [Status.FINISHED],
        Status.FINISHED: [],
    }

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    capacity = models.PositiveIntegerField(default=100)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

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
        return f"{self.title} ({self.status})"

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('زمان شروع باید قبل از زمان پایان باشد.')

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])

    def save(self, *args, **kwargs):
        if not self._state.adding:
            old = Event.objects.filter(pk=self.pk).only('status').first()
            if old and old.status != self.status:
                if not old.can_transition_to(self.status):
                    raise ValidationError(
                        f'تغییر وضعیت از {old.status} به {self.status} مجاز نیست.'
                    )
        self.full_clean(exclude=None)
        super().save(*args, **kwargs)


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
        unique_together = ('event', 'attribute')

    def __str__(self):
        return f"{self.event.title} - {self.attribute.name} : {self.value}"