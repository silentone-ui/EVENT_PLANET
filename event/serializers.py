from rest_framework import serializers
from .models import *


class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.ReadOnlyField(source='attribute.name')


    class Meta:
        model = EventAttributeValue
        fields=['attribute_name','value']


class Eventserializer(serializers.ModelSerializer):
    attributes = EventAttributeValueSerializer(source='attribute_value',many=True,read_only=True)
    organizer_name = serializers.ReadOnlyField(source='organizer.username')

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'location', 'start_time', 
            'end_time', 'image', 'status', 'organizer_name', 'attributes'
        ]
        