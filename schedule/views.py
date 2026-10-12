from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import WeekSchedule
from .utils import now, week_start


@login_required
def schedule_home(request):
    today = now().date()
    start = week_start(today)

    schedule = WeekSchedule.objects.filter(user=request.user, week_start=start).first()

    context = {
        'schedule': schedule,
        'week_start': start,
        'next_sunday': start + timedelta(days=7),
    }
    return render(request, 'schedule/schedule_home.html', context)