from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.schedule_home, name='schedule'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
]