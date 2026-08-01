from django.db import models
from django.contrib.auth.models import User


class TrainingLog(models.Model):
    """Internal record of which skill was trained on which day. Not user-facing history."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_logs')
    skill_key = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skill_key', 'date')