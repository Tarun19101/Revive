from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date

from tasks.models import Task
from habits.models import PlayerHabit
from quests.models import Quest
from bank.models import CashFlow
from bank.views import get_total_money, get_monthly_expense
from events.models import get_events_for_month


@login_required
def dashboard(request):
    profile = request.user.profile
    today = date.today()

    # Today's tasks (pending, created today)
    today_tasks = Task.objects.filter(user=request.user, status=Task.PENDING, created_date=today)

    # Today's habits (scheduled today, from habits app)
    habits = request.user.habits.all()

    # This month's monthly quest
    monthly_quest = Quest.objects.filter(
        user=request.user, category=Quest.MONTHLY, status=Quest.ACTIVE
    ).first()

    # This month's events
    this_month_events = get_events_for_month(request.user, today.year, today.month)

    context = {
        'profile': profile,
        'total_money': get_total_money(request.user),
        'today_tasks': today_tasks,
        'habits': habits,
        'monthly_quest': monthly_quest,
        'monthly_expense': get_monthly_expense(request.user),
        'this_month_events': this_month_events[:5],  # limit to 5 for the card
    }
    return render(request, 'dashboard/dashboard.html', context)