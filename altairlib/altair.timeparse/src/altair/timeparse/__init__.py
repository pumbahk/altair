import parsedatetime
from datetime import datetime, timedelta

__all__ = (
    'parse_time_spec',
    )

def parse_time_spec(spec):
    s = datetime(1900, 1, 1, 0, 0, 0)
    result, _ = parsedatetime.Calendar().parse(spec, s)
    return datetime(
        year=result.tm_year,
        month=result.tm_mon,
        day=result.tm_mday,
        hour=result.tm_hour,
        minute=result.tm_min,
        second=result.tm_sec
        ) - s


