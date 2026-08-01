from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quest, calculate_deadline, check_and_apply_penalties
from .forms import QuestForm


@login_required
def quest_list(request):
    check_and_apply_penalties(request.user)

    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            current_count = Quest.objects.filter(
                user=request.user, category=category, status=Quest.ACTIVE
            ).count()

            if current_count >= Quest.SLOT_LIMITS[category]:
                messages.error(request, 'No open slots in that category.')
            else:
                quest = form.save(commit=False)
                quest.user = request.user
                quest.deadline = calculate_deadline(category, request.user.profile.created_at)
                quest.save()
                messages.success(request, 'Quest added.')
            return redirect('quest_list')
    else:
        form = QuestForm()

    categories = {}
    for cat_key, cat_label in Quest.CATEGORY_CHOICES:
        quests = Quest.objects.filter(user=request.user, category=cat_key, status=Quest.ACTIVE)
        categories[cat_key] = {
            'label': cat_label,
            'quests': quests,
            'count': quests.count(),
            'limit': Quest.SLOT_LIMITS[cat_key],
        }

    context = {'form': form, 'categories': categories}
    return render(request, 'quests/quest_list.html', context)


@login_required
def complete_quest(request, quest_id):
    quest = get_object_or_404(Quest, id=quest_id, user=request.user, status=Quest.ACTIVE)

    xp_earned = Quest.XP_REWARDS[quest.category]
    quest.status = Quest.COMPLETED
    quest.save()

    profile = request.user.profile
    profile.xp += xp_earned
    while profile.xp >= profile.xp_for_next_level:
        profile.xp -= profile.xp_for_next_level
        profile.level += 1
    profile.save()

    messages.success(request, f'Quest completed! +{xp_earned} XP')
    return redirect('quest_list')