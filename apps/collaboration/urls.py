"""
Collaboration app URL patterns.
"""
from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    path('', views.share_manage, name='share_manage'),
    path('create/<int:report_id>/', views.create_share, name='create_share'),
    path('revoke/<int:pk>/', views.revoke_share, name='revoke_share'),
    path('s/<str:token>/', views.share_access, name='share_access'),
]