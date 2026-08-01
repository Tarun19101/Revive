from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import PlayerHabit
from accounts.models import PlayerSkill


@login_required
def habit_list(request):
    habits = request.user.habits.all()
    context = {'habits': habits}
    return render(request, 'habits/habit_list.html', context)


@login_required
def complete_habit(request, habit_id):
    habit = get_object_or_404(PlayerHabit, id=habit_id, user=request.user)

    if not habit.done_today:
        yesterday = date.today() - timedelta(days=1)

        if habit.last_completed == yesterday:
            habit.streak += 1
        else:
            habit.streak = 1

        habit.last_completed = date.today()
        habit.longest_streak = max(habit.longest_streak, habit.streak)
        habit.save()

        # Player XP: flat 2
        profile = request.user.profile
        profile.xp += 2
        while profile.xp >= profile.xp_for_next_level:
            profile.xp -= profile.xp_for_next_level
            profile.level += 1
        profile.save()

        # Skill XP: 5 + 2 * (streak // 5)
        skill_xp = 5 + 2 * (habit.streak // 5)
        skill = PlayerSkill.objects.get(user=request.user, skill_key=habit.skill_key)
        skill.xp += skill_xp
        while skill.xp >= skill.xp_for_next_level:
            skill.xp -= skill.xp_for_next_level
            skill.level += 1
        skill.save()

        messages.success(request, f'{habit.name} done! +2 player XP, +{skill_xp} {skill.name} XP')

    return redirect('habit_list')