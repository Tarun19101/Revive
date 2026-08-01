from django.urls import path
from . import views

urlpatterns = [
    path('quests/', views.quest_list, name='quest_list'),
    path('quests/<int:quest_id>/complete/', views.complete_quest, name='complete_quest'),
]