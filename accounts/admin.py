from django.contrib import admin
from .models import PlayerProfile, PlayerRecord, PlayerSkill

admin.site.register(PlayerProfile)
admin.site.register(PlayerRecord)
admin.site.register(PlayerSkill)