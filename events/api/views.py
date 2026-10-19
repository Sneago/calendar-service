import datetime as dt

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, views
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from events import services
from events.api.serializers import (
    EventCreateSerializer,
    OccurrenceSerializer,
    RenameSerializer,
)
from events.models import Event


def exception_handler(exc, context):
    if isinstance(exc, services.OccurrenceNotFound):
        exc = NotFound()
    return views.exception_handler(exc, context)


class DayFromUrlMixin:
    def get_day(self) -> dt.date:
        """Дата из {year}/{month}/{day} пути; на несуществующую дату — 404."""
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


class OccurrenceCancelView(DayFromUrlMixin, views.APIView):
    @extend_schema(request=None, responses={204: None})
    def post(self, request, pk, **kwargs):
        services.cancel_occurrence(pk, self.get_day())
        return Response(status=status.HTTP_204_NO_CONTENT)


class OccurrenceRenameView(DayFromUrlMixin, generics.GenericAPIView):
    serializer_class = RenameSerializer

    def post(self, request, pk, **kwargs):
        day = self.get_day()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data["name"]
        services.rename_occurrence(pk, day, name)
        return Response({"id": pk, "name": name})
