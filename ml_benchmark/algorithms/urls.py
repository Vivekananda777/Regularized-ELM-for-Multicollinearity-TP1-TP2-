from django.urls import path
from . import views

app_name = 'algorithms'

urlpatterns = [
    path('', views.algorithm_list, name='algorithm_list'),
    path('create/', views.algorithm_create, name='algorithm_create'),
    path('<int:pk>/edit/', views.algorithm_edit, name='algorithm_edit'),
    path('<int:pk>/toggle/', views.algorithm_toggle, name='algorithm_toggle'),
    path('train/', views.train_model, name='train_model'),
    path('history/', views.training_history, name='training_history'),
    path('saved/', views.saved_configs, name='saved_configs'),
    path('<int:algo_pk>/save/', views.save_config, name='save_config'),
    path('saved/<int:pk>/delete/', views.delete_saved_config, name='delete_saved_config'),
]