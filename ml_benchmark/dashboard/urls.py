from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('performance/', views.performance_dashboard, name='performance'),
    path('results/<int:pk>/', views.results_detail, name='results_detail'),
    path('benchmark/schedule/', views.benchmark_schedule, name='benchmark_schedule'),
    path('benchmark/monitor/', views.benchmark_monitor, name='benchmark_monitor'),
    path('benchmark/<int:pk>/run/', views.run_benchmark_job, name='run_benchmark'),
    path('benchmark/<int:pk>/cancel/', views.cancel_job, name='cancel_job'),
    path('api/results/', views.api_results, name='api_results'),
]