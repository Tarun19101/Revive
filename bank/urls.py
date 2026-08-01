from django.urls import path
from . import views

urlpatterns = [
    path('bank/', views.bank_home, name='bank_home'),
    path('bank/<int:entry_id>/clear/', views.clear_loan, name='clear_loan'),
]