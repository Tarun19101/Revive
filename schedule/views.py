from datetime import timedelta

from django.contrib import messages                                  # NEW
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction                    # NEW
from django.shortcuts import redirect, render                        # NEW: redirect
from django.views.decorators.http import require_POST                # NEW

from .models import ScheduleSlot, WeekSchedule                       # NEW: ScheduleSlot
from .utils import DAYS, day_index, hour_label, now, week_start                # NEW: DAYS, hour_label

from tasks.forms import TaskForm
from tasks.models import Task

# NEW: read the limit from the model so the form and the validation can't disagree.
MAX_SLOT_LENGTH = ScheduleSlot._meta.get_field('text').max_length
HOURS = [(h, hour_label(h)) for h in range(24)]                      # NEW


@login_required
def schedule_home(request):
    current = now()                      # CHANGED: keep the full clock reading, not just the date
    today = current.date()
    start = week_start(today)
    today_index = day_index(today)       # NEW

    schedule = WeekSchedule.objects.filter(user=request.user, week_start=start).first()

    # A blank 7 x 24 grid for the "create" form. Field names are slot_<day>_<hour>.
    editor_days = [
        {
            'index': i,
            'name': name,
            'short': name[:3],
            'rows': [{'label': label, 'field': f'slot_{i}_{h}'} for h, label in HOURS],
        }
        for i, name in enumerate(DAYS)
    ]

    # NEW: read-only view of the saved week, with today's current hour flagged.
    view_days = []
    if schedule:
        texts = {(s.day, s.hour): s.text for s in schedule.slots.all()}
        for i, name in enumerate(DAYS):
            view_days.append({
                'index': i,
                'name': name,
                'short': name[:3],
                'rows': [
                    {
                        'label': label,
                        'text': texts.get((i, h), ''),
                        'is_now': i == today_index and h == current.hour,
                    }
                    for h, label in HOURS
                ],
            })

    context = {
        'schedule': schedule,
        'week_start': start,
        'next_sunday': start + timedelta(days=7),
        'today_index': today_index,
        'editor_days': editor_days,
        'view_days': view_days,
        'max_slot_length': MAX_SLOT_LENGTH,
        'tasks': Task.objects.filter(user=request.user, status=Task.PENDING),
        'task_form': TaskForm(),
        'task_xp': Task.XP_REWARD,
    }
    return render(request, 'schedule/schedule_home.html', context)
# NEW: everything from here down
@login_required
@require_POST
def schedule_create(request):
    start = week_start(now().date())

    if WeekSchedule.objects.filter(user=request.user, week_start=start).exists():
        messages.error(request, "This week's schedule is already created.")
        return redirect('schedule')

    slots = []
    for day in range(7):
        for hour in range(24):
            text = request.POST.get(f'slot_{day}_{hour}', '').strip()
            if not text:
                continue
            if len(text) > MAX_SLOT_LENGTH:
                messages.error(
                    request,
                    f"{DAYS[day]}, {hour_label(hour)} is longer than {MAX_SLOT_LENGTH} characters.",
                )
                return redirect('schedule')
            slots.append(ScheduleSlot(day=day, hour=hour, text=text))

    if not slots:
        messages.error(request, 'Fill in at least one hour before saving.')
        return redirect('schedule')

    try:
        with transaction.atomic():
            schedule = WeekSchedule.objects.create(user=request.user, week_start=start)
            for slot in slots:
                slot.schedule = schedule
            ScheduleSlot.objects.bulk_create(slots)
    except IntegrityError:
        # Two tabs saving at once: the unique constraint lets only one through.
        messages.error(request, "This week's schedule is already created.")
        return redirect('schedule')

    messages.success(request, 'Schedule saved for this week.')
    return redirect('schedule')