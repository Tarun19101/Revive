from django.urls import path
from . import views

urlpatterns = [
    path('bank/', views.bank_home, name='bank_home'),
    path('bank/<int:entry_id>/clear/', views.clear_loan, name='clear_loan'),
    path('download-expenses/', views.download_expenses, name='download_expenses'),
    path('download-income/', views.download_income, name='download_income'),
    path('download-loans-taken/', views.download_loans_taken, name='download_loans_taken'),
    path('download-loans-given/', views.download_loans_given, name='download_loans_given'),
]