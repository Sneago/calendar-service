from rest_framework import generics

from events.api.serializers import EventCreateSerializer, OccurrenceSerializer
from events.models import Event


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer


class EventListView(generics.ListAPIView):
    serializer_class = OccurrenceSerializer

    def get_queryset(self):
        return Event.objects.occurring_on(self.kwargs["day"]).by_time_of_day()
