import datetime as dt


class DateConverter:
    regex = r"[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}"

    def to_python(self, path_part: str) -> dt.date:
        """На несуществующую дату вернет 404."""
        year, month, day = map(int, path_part.split("/"))
        return dt.date(year, month, day)

    def to_url(self, day: dt.date) -> str:
        return f"{day.year:04d}/{day.month}/{day.day}"  # noqa: WPS237
