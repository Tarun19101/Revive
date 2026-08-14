from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, OnboardingForm, ProfileEditForm, PlayerRecordForm, AchievementForm
from .models import PlayerRecord, PlayerSkill, PlayerAchievement
from bank.views import get_total_money
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
from .models import PlayerRecord, PlayerSkill, get_attribute_levels
from .constants import ATTRIBUTE_SKILLS


def index(request):
    return render(request, 'accounts/index.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('onboarding')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def onboarding(request):
    profile = request.user.profile

    if profile.onboarding_complete:
        return redirect('dashboard')

    if request.method == 'POST':
        form = OnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            PlayerSkill.objects.filter(user=request.user, skill_key='battle_iq').update(
                choice=form.cleaned_data['martial_art']
            )
            PlayerSkill.objects.filter(user=request.user, skill_key='weapon_mastery').update(
                choice=form.cleaned_data['weapon']
            )
            PlayerSkill.objects.filter(user=request.user, skill_key='hobby').update(
                choice=form.cleaned_data['hobby']
            )

            return redirect('dashboard')
    else:
        form = OnboardingForm(instance=profile)

    return render(request, 'accounts/onboarding.html', {'form': form})

@login_required
def profile(request):
    profile = request.user.profile
    achievements = request.user.achievements

    form = ProfileEditForm(instance=profile)
    achievement_form = AchievementForm(instance=achievements)

    if request.method == 'POST':
        if 'profile_submit' in request.POST:
            form = ProfileEditForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated.')
                return redirect('profile')

        elif 'achievement_submit' in request.POST:
            achievement_form = AchievementForm(request.POST, instance=achievements)
            if achievement_form.is_valid():
                achievement_form.save()
                messages.success(request, 'Achievements updated.')
                return redirect('profile')

    context = {
        'profile': profile,
        'form': form,
        'achievement_form': achievement_form,
        'total_money': get_total_money(request.user),
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def download_records(request):
    records = PlayerRecord.objects.filter(user=request.user).order_by('date')

    lines = [f"{r.date} : {r.text}" for r in records]
    content = "\n\n".join(lines) if lines else "No records yet."

    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="{request.user.username}_records.md"'
    return response

@login_required
def progress(request):
    attribute_levels = get_attribute_levels(request.user)
    skills = {s.skill_key: s for s in request.user.skills.all()}

    grouped = []
    for attr_key, attr_data in attribute_levels.items():
        skill_keys = ATTRIBUTE_SKILLS[attr_key]
        attr_skills = [skills[sk] for sk in skill_keys if sk in skills]
        grouped.append({
            'name': attr_data['name'],
            'level': attr_data['level'],
            'skills': attr_skills,
        })

    context = {'grouped': grouped}
    return render(request, 'accounts/progress.html', context)