from django.urls import path
from . import views

urlpatterns = [
    path('deepwork/', views.deepwork_home, name='deepwork_home'),
    path('deepwork/complete/<str:skill_key>/', views.complete_training, name='complete_training'),
]