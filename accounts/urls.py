from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('profile/', views.profile, name='profile'),
    path('progress/', views.progress, name='progress'),
    path('profile/records/download/', views.download_records, name='download_records'),
]