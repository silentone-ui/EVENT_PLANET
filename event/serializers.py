from rest_framework import serializers
from .models import *


class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.ReadOnlyField(source='attribute.name')

    class Meta:
        model = EventAttributeValue
        fields = ['id', 'attribute_name', 'value']


class EventSerializer(serializers.ModelSerializer):
    attributes = EventAttributeValueSerializer(source='attribute_values', many=True, read_only=True)
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
            'end_time', 'image', 'capacity', 'status',
            'organizer_firstname', 'attributes', 'attributes_data'
        ]
        read_only_fields = ['status', 'organizer_phone']

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes_data', [])
        validated_data['status'] = Event.Status.DRAFT
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

            EventAttributeValue.objects.create(
                event=event,
                attribute=attribute,
                value=value
            )

        return event


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