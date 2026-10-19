from rest_framework import serializers

from events.models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "start_at", "period"]  # noqa: WPS226
        extra_kwargs = {
            "name": {"write_only": True},
            "start_at": {"write_only": True},
            "period": {"write_only": True},
        }


class OccurrenceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="occurrence_name")

    class Meta:
        model = Event
        fields = ["id", "name"]


class RenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name"]
