from django.urls import path

from core.views import views_frontend_v1

urlpatterns = [
    path('change/<int:day_entry_id>/', views_frontend_v1.change_view, name='frontend-v1-change-view'),
    path(
        'scrum-entry/<int:scrum_entry_id>/start-timer', views_frontend_v1.start_timer_view,
        name='frontend-v1-start-timer'
    ),
    path(
        'scrum-entry/<int:scrum_entry_id>/add-manual-time', views_frontend_v1.add_manual_time_view,
        name='frontend-v1-add-manual-time'
    ),
    path(
        'scrum-entry/<int:scrum_entry_id>/stop-timer/<int:time_log_id>', views_frontend_v1.stop_timer_view,
        name='frontend-v1-stop-timer'
    ),
    path(
        'scrum-entry/<int:scrum_entry_id>/set-status', views_frontend_v1.set_status_view,
        name='frontend-v1-set-status'
    ),
]
