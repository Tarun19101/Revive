from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Task(models.Model):
    IMPORTANT = 'important'
    CASUAL = 'casual'
    TYPE_CHOICES = [
        (IMPORTANT, 'Important'),
        (CASUAL, 'Casual'),
    ]

    PENDING = 'pending'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    ]

    ON_TIME_XP = {
        IMPORTANT: 10,
        CASUAL: 5,
    }
    LATE_XP = {
        IMPORTANT: 5,
        CASUAL: 2,
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    @property
    def is_late(self):
        return self.created_date != date.today()

    @property
    def xp_reward(self):
        return self.LATE_XP[self.type] if self.is_late else self.ON_TIME_XP[self.type]

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"