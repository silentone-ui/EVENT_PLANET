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
    class DataType(models.TextChoices):
        TEXT = 'text', 'Text'
        INT = 'int', 'Integer'
        BOOL = 'bool', 'Boolean'
        DATE = 'date', 'Date'

    name = models.CharField(max_length=100, unique=True)
    data_type = models.CharField(max_length=10, choices=DataType.choices, default=DataType.TEXT)

    def __str__(self):
        return f"{self.name} ({self.data_type})"


class EventAttributeValue(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(EventAttribute, on_delete=models.CASCADE, related_name='event_values')
    value_text = models.CharField(max_length=255, null=True, blank=True)
    value_int = models.IntegerField(null=True, blank=True)
    value_bool = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'attribute')

    def __str__(self):
        return f"{self.attribute.name} -> {self.value}"

    @property
    def value(self):
        if not self.attribute_id:
            return None
        dt = self.attribute.data_type
        if dt == EventAttribute.DataType.TEXT:
            return self.value_text
        if dt == EventAttribute.DataType.INT:
            return self.value_int
        if dt == EventAttribute.DataType.BOOL:
            return self.value_bool
        if dt == EventAttribute.DataType.DATE:
            return self.value_date
        return None

    def clean(self):
        super().clean()
        if not self.attribute_id or not self.event_id:
            return
        dt = self.attribute.data_type
        if dt == EventAttribute.DataType.TEXT:
            if not self.value_text:
                raise ValidationError('برای ویژگی متنی باید value_text پر شود.')
            if self.value_int is not None or self.value_bool is not None or self.value_date is not None:
                raise ValidationError('فقط value_text باید پر باشد، بقیه باید خالی باشند.')
        elif dt == EventAttribute.DataType.INT:
            if self.value_int is None:
                raise ValidationError('برای ویژگی عددی باید value_int پر شود.')
            if self.value_text or self.value_bool is not None or self.value_date is not None:
                raise ValidationError('فقط value_int باید پر باشد، بقیه باید خالی باشند.')
        elif dt == EventAttribute.DataType.BOOL:
            if self.value_bool is None:
                raise ValidationError('برای ویژگی بولین باید value_bool پر شود.')
            if self.value_text or self.value_int is not None or self.value_date is not None:
                raise ValidationError('فقط value_bool باید پر باشد، بقیه باید خالی باشند.')
        elif dt == EventAttribute.DataType.DATE:
            if self.value_date is None:
                raise ValidationError('برای ویژگی تاریخی باید value_date پر شود.')
            if self.value_text or self.value_int is not None or self.value_bool is not None:
                raise ValidationError('فقط value_date باید پر باشد، بقیه باید خالی باشند.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class Registration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} -> {self.event.title}"

    def clean(self):
        super().clean()
        if not self.event_id or not self.user_id:
            return
        if self.event.status != Event.Status.PUBLISHED:
            raise ValidationError('ثبت‌نام فقط برای رویداد منتشرشده مجاز است.')
        if self.event.organizer_id == self.user_id:
            raise ValidationError('برگزارکننده نمی‌تواند در رویداد خودش ثبت‌نام کند.')
        qs = Registration.objects.filter(event=self.event)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.count() >= self.event.capacity:
            raise ValidationError('ظرفیت رویداد تکمیل شده است.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class Stage(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['start_time','order']

    def __str__(self):
        return f"{self.title} ({self.event.title})"

    def clean(self):
        super().clean()
        if not self.start_time or not self.end_time:
            return
        if self.start_time >= self.end_time:
            raise ValidationError('زمان شروع بخش باید قبل از زمان پایان باشد.')
        if self.event_id:
            if self.start_time < self.event.start_time or self.end_time > self.event.end_time:
                raise ValidationError('ساعت بخش باید داخل بازه زمانی ایونت باشد.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StageAssignment(models.Model):
    class RoleChoices(models.TextChoices):
        SPEAKER = 'speaker', 'Speaker'
        JUDGE = 'judge', 'Judge'
        COACH = 'coach', 'Coach'

    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stage_assignments'
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.SPEAKER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('stage', 'user', 'role')

    def __str__(self):
        return f"{self.user} as {self.role} in {self.stage.title}"


class Feedback(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} -> {self.event.title} ({self.rating})"

    def clean(self):
        super().clean()
        if not self.event_id or not self.user_id:
            return
        if self.event.status != Event.Status.FINISHED:
            raise ValidationError('بازخورد فقط وقتی مجاز است که رویداد finished شده باشد.')
        if self.event.organizer_id == self.user_id:
            raise ValidationError('برگزارکننده نمی‌تواند بازخورد ثبت کند.')
        if not Registration.objects.filter(event=self.event, user_id=self.user_id).exists():
            raise ValidationError('فقط شرکت‌کننده‌ای که ثبت‌نام کرده می‌تواند بازخورد بدهد.')
        if not 1 <= self.rating <= 5:
            raise ValidationError('امتیاز باید بین ۱ تا ۵ باشد.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Result(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='result'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"نتیجه {self.event.title}"

    def clean(self):
        super().clean()
        if not self.event_id:
            return
        if self.event.status != Event.Status.FINISHED:
            raise ValidationError('انتشار نتیجه فقط وقتی مجاز است که رویداد finished شده باشد.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)