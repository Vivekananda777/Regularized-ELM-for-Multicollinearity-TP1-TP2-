from django.urls import path
from . import views

app_name = 'exports'

urlpatterns = [
    path('results/pdf/', views.export_results_pdf, name='export_results_pdf'),
    path('diagnostic/<int:pk>/pdf/', views.export_diagnostic_pdf, name='export_diagnostic_pdf'),
    path('result/<int:result_id>/plot/', views.export_plot_png, name='export_plot'),
]