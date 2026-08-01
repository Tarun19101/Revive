from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date
from .constants import DAY_SKILLS, TRAINING_XP
from .models import TrainingLog
from accounts.models import PlayerSkill


@login_required
def deepwork_home(request):
    today = date.today()
    weekday = today.weekday()
    scheduled_keys = DAY_SKILLS.get(weekday, [])

    trained_today = set(
        TrainingLog.objects.filter(user=request.user, date=today)
        .values_list('skill_key', flat=True)
    )

    available_keys = [k for k in scheduled_keys if k not in trained_today]
    available_skills = PlayerSkill.objects.filter(user=request.user, skill_key__in=available_keys)
    completed_skills = PlayerSkill.objects.filter(user=request.user, skill_key__in=trained_today & set(scheduled_keys))

    context = {
        'available_skills': available_skills,
        'completed_skills': completed_skills,
        'all_done': len(available_keys) == 0 and len(scheduled_keys) > 0,
    }
    return render(request, 'deepwork/deepwork_home.html', context)


@login_required
def complete_training(request, skill_key):
    """Called via JS fetch when the 2hr timer hits zero."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    today = date.today()
    weekday = today.weekday()
    scheduled_keys = DAY_SKILLS.get(weekday, [])

    if skill_key not in scheduled_keys:
        return JsonResponse({'error': 'Not scheduled today'}, status=400)

    already_done = TrainingLog.objects.filter(user=request.user, skill_key=skill_key, date=today).exists()
    if already_done:
        return JsonResponse({'error': 'Already trained today'}, status=400)

    TrainingLog.objects.create(user=request.user, skill_key=skill_key, date=today)

    skill = PlayerSkill.objects.get(user=request.user, skill_key=skill_key)
    skill.xp += TRAINING_XP
    while skill.xp >= skill.xp_for_next_level:
        skill.xp -= skill.xp_for_next_level
        skill.level += 1
    skill.save()

    return JsonResponse({'success': True, 'xp_earned': TRAINING_XP, 'skill_name': skill.name})