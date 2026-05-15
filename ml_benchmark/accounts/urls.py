from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('register/',views.register_view,name='register'),
    path('profile/',views.profile,name='profile'),
    path('users/',views.user_management,name='user_management'),
    path('users/create/',views.create_user,name='create_user'),
    path('users/<int:user_id>/edit/',views.edit_user,name='edit_user'),
    path('users/<int:user_id>/revoke/',views.revoke_access,name='revoke_access'),
    path('users/<int:user_id>/restore/',views.restore_access,name='restore_access'),
    path('audit-log/',views.audit_log,name='audit_log'),
]