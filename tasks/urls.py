from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
]