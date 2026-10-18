import datetime as dt

from rest_framework import generics
from rest_framework.exceptions import NotFound

from events.api.serializers import EventCreateSerializer, OccurrenceSerializer
from events.models import Event


class DayFromUrlMixin:
    def get_day(self) -> dt.date:
        """Дата из `{year}/{month}/{day}` пути; на несуществующую дату — 404."""
        try:
            return dt.date(self.kwargs["year"], self.kwargs["month"], self.kwargs["day"])  # noqa: WPS221
        except ValueError, OverflowError:
            raise NotFound from None


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer


class EventListView(DayFromUrlMixin, generics.ListAPIView):
    serializer_class = OccurrenceSerializer

    def get_queryset(self):
        return Event.objects.occurring_on(self.get_day()).by_time_of_day()
