from django.urls import path
from . import views

app_name = 'datasets'

urlpatterns = [
    path('', views.dataset_list, name='dataset_list'),
    path('upload/', views.dataset_upload, name='dataset_upload'),
    path('<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('<int:pk>/deprecate/', views.dataset_deprecate, name='dataset_deprecate'),
    path('<int:pk>/restore/', views.dataset_restore, name='dataset_restore'),
    path('<int:pk>/preview/', views.dataset_preview, name='dataset_preview'),
    path('experiment/new/', views.new_experiment, name='new_experiment'),
]