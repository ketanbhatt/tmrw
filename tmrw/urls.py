from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('nested_admin/', include('nested_admin.urls')),
    path('core/', include('core.urls')),
]
