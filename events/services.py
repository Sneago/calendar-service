import datetime as dt

from django.db import transaction

from events.models import Event, OccurrenceOverride
from events.querysets import SECONDS_PER_DAY, day_number


class OccurrenceNotFound(Exception):  # noqa: N818
    """У серии нет вхождения в этот день, или самой серии нет."""


def _lock_occurrence(event_id: int, day: dt.date) -> Event:
    """Блокирует серию и проверяет вхождение."""
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


@transaction.atomic
def cancel_occurrences_from(event_id: int, day: dt.date) -> None:
    event = _lock_occurrence(event_id, day)
    if day_number(day) == event.start_at // SECONDS_PER_DAY:
        event.delete()
    else:
        event.until = day
        event.save(update_fields=["until"])
        event.overrides.filter(date__gte=day).delete()


@transaction.atomic
def rename_occurrence(event_id: int, day: dt.date, name: str) -> None:
    event = _lock_occurrence(event_id, day)
    OccurrenceOverride.objects.update_or_create(
        event=event,
        date=day,
        defaults={"name": name},
    )
