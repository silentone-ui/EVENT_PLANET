from rest_framework import serializers
from .models import *


class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.ReadOnlyField(source='attribute.name')


    class Meta:
        model = EventAttributeValue
        fields=['id','attribute_name','value']


class Eventserializer(serializers.ModelSerializer):
    attributes = EventAttributeValueSerializer(source='attribute_values',many=True,read_only=True)
    organizer_name = serializers.ReadOnlyField(source='organizer.username')

    attributes_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
    )
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'location', 'start_time', 
            'end_time', 'image', 'status', 'organizer_name', 'attributes','attributes_data'
        ]
        read_only_fields = ['organizer','created_at']

    def create(self, validated_data):

        attributes_data = validated_data.pop('attributes_data', [])
        validated_data['status'] = Event.Status.DRAFT
        event = Event.objects.create(**validated_data)

        for attr_data in attributes_data:
            attribute_id = attr_data.get('attribute')
            value = attr_data.get('value')
                
            try:
                attribute = EventAttribute.objects.get(id=attribute_id)
                EventAttributeValue.objects.create(
                    event=event,
                    attribute=attribute,
                    value=value
                )
            except EventAttribute.DoesNotExist:
                pass 

        return event

