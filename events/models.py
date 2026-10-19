from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from events.querysets import EventQuerySet

NAME_MAX_LENGTH = 255
MAX_START_AT = 253402300799  # 9999-12-31T23:59:59Z


class Event(models.Model):
    """Разовое событие или серия, повторяющаяся каждые period дней."""

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    start_at = models.BigIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_START_AT),
        ],
    )
    period = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    # день until в серию не входит
    until = models.DateField(
        null=True,
        blank=True,
    )

    objects = EventQuerySet.as_manager()  # noqa: WPS110

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(period__gte=1) | models.Q(period__isnull=True),
                name="event_period_positive_or_null",
            ),
            models.CheckConstraint(
                condition=models.Q(start_at__gte=0),
                name="event_start_at_non_negative",
            ),
        ]
        indexes = [
            models.Index(
                fields=["start_at"],
                condition=models.Q(period__isnull=True),
                name="event_single_start_at",
            ),
            models.Index(
                fields=["start_at"],
                condition=models.Q(period__isnull=False),
                name="event_series_start_at",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class OccurrenceOverride(models.Model):
    """Изменение одного вхождения серии: отмена или переименование."""

    # индекс по event даёт UniqueConstraint(event, date)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="overrides",
        db_index=False,
    )
    date = models.DateField()
    name = models.CharField(  # noqa: DJ001
        max_length=NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "date"],
                name="override_event_date_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_id}: {self.date}"
