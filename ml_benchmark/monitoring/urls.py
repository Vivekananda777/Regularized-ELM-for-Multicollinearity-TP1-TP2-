from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.monitoring_dashboard, name='dashboard'),
    path('alert/<int:pk>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('api/status/', views.module_status_api, name='status_api'),
]