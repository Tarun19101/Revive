from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, PlayerSkill, PlayerAchievement
from .constants import SKILL_CATALOG


@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    if created:
        PlayerProfile.objects.create(user=instance)
        PlayerAchievement.objects.create(user=instance)
        for skill_key in SKILL_CATALOG:
            PlayerSkill.objects.create(user=instance, skill_key=skill_key)