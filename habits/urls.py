from django.urls import path
from . import views

urlpatterns = [
    path('habits/', views.habit_list, name='habit_list'),
    path('habits/<int:habit_id>/complete/', views.complete_habit, name='complete_habit'),
]