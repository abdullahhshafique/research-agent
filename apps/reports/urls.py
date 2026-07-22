"""
Reports app URL patterns.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('<int:pk>/preview/', views.report_preview, name='report_preview'),
    path('<int:pk>/download/', views.report_download, name='report_download'),
]