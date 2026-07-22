from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.utils.health import health_check  # FIXED: was 'from utils.health import health_check'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('research/', include('apps.research.urls', namespace='research')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('history/', include('apps.history.urls', namespace='history')),
    path('collaboration/', include('apps.collaboration.urls', namespace='collaboration')),
    path('templates/', include('apps.templates_app.urls', namespace='templates')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)