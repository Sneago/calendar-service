import datetime as dt
from typing import Self

from django.db import models
from django.db.models.functions import Coalesce

SECONDS_PER_DAY = 86400
EPOCH = dt.date(1970, 1, 1)  # noqa: WPS432


class EventQuerySet(models.QuerySet):
    def occurring_on(self, day: dt.date) -> Self:
        day_number = (day - EPOCH).days
        day_start = day_number * SECONDS_PER_DAY
        day_end = day_start + SECONDS_PER_DAY
        days_since_start = day_number - models.F("start_at") / SECONDS_PER_DAY
        override = models.FilteredRelation(
            "overrides",
            condition=models.Q(overrides__date=day),
        )
        return (
            self
            .alias(
                days_into_period=days_since_start % models.F("period"),
                override=override,
            )
            .annotate(
                occurrence_name=Coalesce("override__name", "name"),
            )
            .filter(
                # period__isnull в обеих ветках: так Postgres выбирает частичные индексы
                models.Q(period__isnull=True, start_at__gte=day_start, start_at__lt=day_end)
                | models.Q(period__isnull=False, start_at__lt=day_end, days_into_period=0),
                models.Q(override__isnull=True) | models.Q(override__is_cancelled=False),
            )
        )

    def by_time_of_day(self) -> Self:
        """Сортировка по времени суток события."""
        return self.order_by(models.F("start_at") % SECONDS_PER_DAY, "pk")
