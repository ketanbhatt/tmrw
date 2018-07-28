from django.urls import path

from core.views import views_frontend_v1

urlpatterns = [
    path('change/<int:day_entry_id>/', views_frontend_v1.change_view, name='frontend-v1-change-view'),
]
