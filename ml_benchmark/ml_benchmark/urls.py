from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('datasets/', include('datasets.urls')),
    path('algorithms/', include('algorithms.urls')),
    path('diagnostics/', include('diagnostics.urls')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('exports/', include('exports.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('', include('dashboard.urls')),  # no namespace here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)