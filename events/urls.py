from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
]