from django.urls import path

from . import views

urlpatterns = [
    path('day-entry/html/<int:day_entry_id>/', views.day_entry_html, name='day-entry-html'),
]
