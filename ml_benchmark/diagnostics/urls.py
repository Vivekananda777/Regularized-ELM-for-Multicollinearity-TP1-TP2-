from django.urls import path
from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('run/', views.run_diagnostic, name='run_diagnostic'),
    path('report/<int:pk>/', views.report_detail, name='report_detail'),
]