from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()

    today = date.today()
    user_tasks = Task.objects.filter(user=request.user, status=Task.PENDING)

    today_important = user_tasks.filter(type=Task.IMPORTANT, created_date=today)
    today_casual = user_tasks.filter(type=Task.CASUAL, created_date=today)
    pending = user_tasks.exclude(created_date=today)

    context = {
        'form': form,
        'today_important': today_important,
        'today_casual': today_casual,
        'pending': pending,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if task.status == Task.PENDING:
        xp_earned = task.xp_reward

        task.status = Task.COMPLETED
        task.save()

        profile = request.user.profile
        profile.xp += xp_earned

        while profile.xp >= profile.xp_for_next_level:
            profile.xp -= profile.xp_for_next_level
            profile.level += 1

        profile.save()

        messages.success(request, f'Task completed! +{xp_earned} XP')

    return redirect('task_list')