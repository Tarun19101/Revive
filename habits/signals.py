from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerHabit
from .constants import HABIT_CATALOG


@receiver(post_save, sender=User)
def create_player_habits(sender, instance, created, **kwargs):
    if created:
        for habit_key in HABIT_CATALOG:
            PlayerHabit.objects.create(user=instance, habit_key=habit_key)