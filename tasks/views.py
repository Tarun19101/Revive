from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Task
from .forms import TaskForm


@login_required
@require_POST
def add_task(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
    else:
        messages.error(request, 'Enter a task title.')
    return redirect('schedule')


@login_required
@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    # Flip pending -> completed in one query, so a double submit pays out once.
    if Task.objects.filter(pk=task.pk, status=Task.PENDING).update(status=Task.COMPLETED):
        profile = request.user.profile
        profile.xp += Task.XP_REWARD

        while profile.xp >= profile.xp_for_next_level:
            profile.xp -= profile.xp_for_next_level
            profile.level += 1

        profile.save()

        messages.success(request, f'Task completed! +{Task.XP_REWARD} XP')

    return redirect('schedule')