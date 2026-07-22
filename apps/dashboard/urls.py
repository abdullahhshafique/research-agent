"""
Dashboard app URL patterns.
"""
from django.urls import path
from . import views
from . import cleanup_views
from . import views_api_keys

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('keys/', views_api_keys.api_keys, name='api_keys'),
    path('keys/rotate/', views_api_keys.rotate_api_key, name='rotate_api_key'),
    path('keys/deactivate/', views_api_keys.deactivate_api_key, name='deactivate_api_key'),
    path('keys/status/', views_api_keys.api_key_status_api, name='api_key_status_api'),
    path('cleanup/', cleanup_views.cleanup_view, name='cleanup_view'),
    path('queue/', views.queue_monitor, name='queue_monitor'),
    path('logs/', views.error_logs, name='error_logs'),
    path('api/cache-stats/', cleanup_views.cache_stats_api, name='cache_stats_api'),
    path('api/queue/', views.queue_api, name='queue_api'),
    path('api/log-stats/', views.log_stats_api, name='log_stats_api'),
    # User management API endpoints
    path('api/users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),
    path('api/users/<int:user_id>/role/', views.update_user_role, name='update_user_role'),
    path('api/users/<int:user_id>/quota/', views.update_user_quota, name='update_user_quota'),
]