from django.urls import path

from core.views import views_base

urlpatterns = [
    path('day-entry/html/<int:day_entry_id>/', views_base.day_entry_html, name='day-entry-html'),
]
