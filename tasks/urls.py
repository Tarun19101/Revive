from django.urls import path
from . import views

urlpatterns = [
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
]