from django.db import models
from django.contrib.auth.models import User
from datetime import date
from .constants import SKILL_CATALOG, ATTRIBUTE_SKILLS, ATTRIBUTES

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def bmi(self):
        if not self.weight_kg or not self.height_cm:
            return None
        height_m = float(self.height_cm) / 100
        return round(float(self.weight_kg) / (height_m ** 2), 1)

    @property
    def onboarding_complete(self):
        return all([self.date_of_birth, self.weight_kg, self.height_cm])

    @property
    def xp_for_next_level(self):
        # Simple scaling formula: each level requires more XP than the last
        return (self.level) * (self.level + 1) * 25

    @property
    def xp_progress_percent(self):
        return min(100, int((self.xp / self.xp_for_next_level) * 100))

class PlayerRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records')
    date = models.DateField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

from .constants import SKILL_CATALOG, ATTRIBUTE_SKILLS, ATTRIBUTES


class PlayerSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill_key = models.CharField(max_length=50)
    level = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)
    choice = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'skill_key')

    @property
    def name(self):
        return SKILL_CATALOG[self.skill_key]['name']

    @property
    def attribute_key(self):
        return SKILL_CATALOG[self.skill_key]['attribute']

    @property
    def choice_type(self):
        return SKILL_CATALOG[self.skill_key]['choice_type']

    @property
    def xp_for_next_level(self):
        return (self.level + 1) * 100

    @property
    def xp_progress_percent(self):
        return min(100, int((self.xp / self.xp_for_next_level) * 100))

    @property
    def display_name(self):
        return f"{self.name} ({self.choice})" if self.choice else self.name

    def __str__(self):
        return f"{self.user.username} - {self.name}"

def get_attribute_levels(user):
    """Returns dict: attribute_key -> {name, level} computed from PlayerSkill levels."""
    skills = {s.skill_key: s for s in user.skills.all()}
    result = {}
    for attr_key, attr_name in ATTRIBUTES.items():
        skill_keys = ATTRIBUTE_SKILLS[attr_key]
        levels = [skills[sk].level for sk in skill_keys if sk in skills]
        if len(levels) == 1:
            attr_level = levels[0]
        else:
            total = sum(levels)
            if total % 2 != 0:
                total -= 1
            attr_level = total // 2
        result[attr_key] = {'name': attr_name, 'level': attr_level}
    return result