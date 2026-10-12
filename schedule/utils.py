from datetime import date, datetime, timedelta

# Weeks run Sunday to Saturday, so day 0 is Sunday.
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def now():
    """Single place to read the clock, so tests can pin it."""
    return datetime.now()


def week_start(d: date) -> date:
    """The Sunday that begins the week containing d."""
    return d - timedelta(days=(d.weekday() + 1) % 7)


def day_index(d: date) -> int:
    """0 = Sunday ... 6 = Saturday."""
    return (d.weekday() + 1) % 7


def _clock(hour: int) -> str:
    hour %= 24
    suffix = 'am' if hour < 12 else 'pm'
    return f"{hour % 12 or 12}:00 {suffix}"


def hour_label(hour: int) -> str:
    """0 -> '12:00 am to 1:00 am', 23 -> '11:00 pm to 12:00 am'."""
    return f"{_clock(hour)} to {_clock(hour + 1)}"