from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import month_name
from .models import Event, get_events_for_month, get_calendar_grid
from .forms import EventForm


@login_required
def event_list(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()

    today = date.today()
    this_year, this_month = today.year, today.month
    next_month = this_month + 1 if this_month < 12 else 1
    next_month_year = this_year if this_month < 12 else this_year + 1

    context = {
        'form': form,
        'grid': get_calendar_grid(this_year, this_month),
        'month_label': f"{month_name[this_month]} {this_year}",
        'today_day': today.day,
        'this_month_events': get_events_for_month(request.user, this_year, this_month),
        'next_month_events': get_events_for_month(request.user, next_month_year, next_month),
        'next_month_label': month_name[next_month],
    }
    return render(request, 'events/event_list.html', context)


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    event.delete()
    return redirect('event_list')


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})