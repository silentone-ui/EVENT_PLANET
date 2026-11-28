from rest_framework import serializers
from .models import *
import datetime
from django.db import transaction

class AnyValueField(serializers.Field):
    def to_representation(self, value):
        return value
    def to_internal_value(self, data):
        return data


class EventAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttribute
        fields = ['id', 'name', 'data_type']

class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.ReadOnlyField(source='attribute.name')
    data_type = serializers.ReadOnlyField(source='attribute.data_type')
    display_value = serializers.ReadOnlyField(source='value')
    value = AnyValueField(write_only=True)

    class Meta:
        model = EventAttributeValue
        fields = ['id', 'event', 'attribute', 'attribute_name', 'data_type', 'display_value', 'value']

    def validate(self, attrs):
        attr = attrs.get('attribute')
        if attr is None and self.instance is not None:
            attr = self.instance.attribute
        if attr is None:
            raise serializers.ValidationError('ویژگی مشخص نیست.')
        if 'value' not in attrs:
            raise serializers.ValidationError('فیلد value الزامی است.')

        val = attrs.pop('value')
        dt = attr.data_type

        attrs['value_text'] = None
        attrs['value_int'] = None
        attrs['value_bool'] = None
        attrs['value_date'] = None

        if dt == EventAttribute.DataType.TEXT:
            if not isinstance(val, str):
                raise serializers.ValidationError('برای این ویژگی باید رشته بفرستی.')
            attrs['value_text'] = val
        elif dt == EventAttribute.DataType.INT:
            if not isinstance(val, int) or isinstance(val, bool):
                raise serializers.ValidationError('برای این ویژگی باید عدد صحیح بفرستی.')
            attrs['value_int'] = val
        elif dt == EventAttribute.DataType.BOOL:
            if not isinstance(val, bool):
                raise serializers.ValidationError('برای این ویژگی باید true یا false بفرستی.')
            attrs['value_bool'] = val
        elif dt == EventAttribute.DataType.DATE:
            if isinstance(val, str):
                try:
                    val = datetime.date.fromisoformat(val)
                except ValueError:
                    raise serializers.ValidationError('تاریخ باید مثل 2026-12-10 باشد.')
            if not isinstance(val, datetime.date):
                raise serializers.ValidationError('برای این ویژگی باید تاریخ بفرستی.')
            attrs['value_date'] = val

        return attrs

class EventSerializer(serializers.ModelSerializer):
    attributes = EventAttributeValueSerializer(source='attribute_values', many=True, read_only=True)
    organizer = serializers.ReadOnlyField(source='organizer.phone')
    organizer_firstname = serializers.ReadOnlyField(source='organizer.first_name')

    attributes_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'location', 'start_time',
            'end_time', 'image', 'capacity', 'status','organizer',
            'organizer_firstname', 'attributes', 'attributes_data'
        ]
        read_only_fields = ['status', 'organizer','organizer_firstname']

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes_data', [])
        validated_data['status'] = Event.Status.DRAFT
        with transaction.atomic():
            event = Event.objects.create(**validated_data)

            for attr_data in attributes_data:
                attribute_id = attr_data.get('attribute')
                value = attr_data.get('value')
                if not attribute_id or value is None:
                    raise serializers.ValidationError('هر ویژگی باید attribute و value داشته باشد.')
                try:
                    attribute = EventAttribute.objects.get(id=attribute_id)
                except EventAttribute.DoesNotExist:
                    raise serializers.ValidationError(f'ویژگی با id={attribute_id} وجود ندارد.')

                tmp = EventAttributeValueSerializer(data={
                    'event': event.id,
                    'attribute': attribute.id,
                    'value': value
                })
                tmp.is_valid(raise_exception=True)
                tmp.save()
        return event
    def update(self, instance, validated_data):
        if 'status' in self.initial_data:
            raise serializers.ValidationError('تغییر وضعیت فقط از طریق change-status مجاز است.')
        validated_data.pop('attributes_data', None)
        validated_data.pop('status', None)
        return super().update(instance, validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    user_phone = serializers.ReadOnlyField(source='user.phone')
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Registration
        fields = ['id', 'event', 'event_title', 'user_phone', 'created_at']
        read_only_fields = ['event_title', 'user_phone', 'created_at']


class StageSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Stage
        fields = ['id', 'event', 'event_title', 'title', 'description', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['event_title', 'created_at']


class StageAssignmentSerializer(serializers.ModelSerializer):
    user_phone = serializers.ReadOnlyField(source='user.phone')
    stage_title = serializers.ReadOnlyField(source='stage.title')

    class Meta:
        model = StageAssignment
        fields = ['id', 'stage', 'stage_title', 'user', 'user_phone', 'role']
        read_only_fields = ['stage_title', 'user_phone']


class FeedbackSerializer(serializers.ModelSerializer):
    user_phone = serializers.ReadOnlyField(source='user.phone')
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Feedback
        fields = ['id', 'event', 'event_title', 'user_phone', 'rating', 'comment', 'created_at']
        read_only_fields = ['event_title', 'user_phone', 'created_at']


class ResultSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Result
        fields = ['id', 'event', 'event_title', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['event_title', 'created_at', 'updated_at']