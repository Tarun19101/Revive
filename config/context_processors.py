from schedule.utils import now


def current_time(request):
    """Makes `current_time` available to every template (the page title line uses it)."""
    return {'current_time': now()}