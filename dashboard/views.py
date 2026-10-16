from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import get_attribute_levels
from tasks.models import Task
from habits.models import PlayerHabit
from quests.models import Quest
from bank.models import CashFlow
from bank.views import get_total_money, get_monthly_expense
from schedule.models import ScheduleSlot
from schedule.utils import day_index, hour_label, now, week_start


def _planned_text(user, moment):
    """What the player planned for the hour containing `moment`, or '' if nothing."""
    slot = ScheduleSlot.objects.filter(
        schedule__user=user,
        schedule__week_start=week_start(moment.date()),
        day=day_index(moment.date()),
        hour=moment.hour,
    ).first()
    return slot.text if slot else ''


@login_required
def dashboard(request):
    profile = request.user.profile
    current = now()
    upcoming = current + timedelta(hours=1)

    # Pending tasks (one list, newest first)
    pending_tasks = Task.objects.filter(user=request.user, status=Task.PENDING)

    # Today's habits (scheduled today, from habits app)
    habits = request.user.habits.all()

    # This month's monthly quest
    monthly_quest = Quest.objects.filter(
        user=request.user, category=Quest.MONTHLY, status=Quest.ACTIVE
    ).first()

    context = {
        'profile': profile,
        'total_money': get_total_money(request.user),
        'pending_tasks': pending_tasks[:5],
        'pending_task_count': pending_tasks.count(),
        'habits': habits,
        'monthly_quest': monthly_quest,
        'monthly_expense': get_monthly_expense(request.user),
        'hour_now': {'label': hour_label(current.hour), 'text': _planned_text(request.user, current)},
        'hour_next': {'label': hour_label(upcoming.hour), 'text': _planned_text(request.user, upcoming)},
        'attribute_levels': get_attribute_levels(request.user),
    }
    return render(request, 'dashboard/dashboard.html', context)