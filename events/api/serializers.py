from rest_framework import serializers

from events.models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "start_at", "period"]
        extra_kwargs = {
            "name": {"write_only": True},
            "start_at": {"write_only": True},
            "period": {"write_only": True},
        }


class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name"]
