import datetime as dt

from django.db import transaction

from events.models import Event, OccurrenceOverride


class OccurrenceNotFound(Exception):  # noqa: N818
    """У серии нет вхождения в этот день, или самой серии нет."""


def _lock_occurrence(event_id: int, day: dt.date) -> Event:
    """Блокирует серию и проверяет вхождение"""
    try:
        event = Event.objects.select_for_update().get(pk=event_id)
    except Event.DoesNotExist:
        raise OccurrenceNotFound from None
    if not Event.objects.occurring_on(day).filter(pk=event_id).exists():
        raise OccurrenceNotFound
    return event


@transaction.atomic
def cancel_occurrence(event_id: int, day: dt.date) -> None:
    event = _lock_occurrence(event_id, day)
    if event.period is None:
        event.delete()
    else:
        OccurrenceOverride.objects.update_or_create(
            event=event,
            date=day,
            defaults={"is_cancelled": True},
        )
