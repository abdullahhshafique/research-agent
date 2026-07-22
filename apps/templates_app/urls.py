"""
Templates app URL patterns.
"""
from django.urls import path
from . import views

app_name = 'templates'

urlpatterns = [
    path('', views.templates_list, name='templates_list'),
    path('create/', views.template_create, name='template_create'),
    path('<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('<int:pk>/use/', views.template_use, name='template_use'),
    path('<int:pk>/detail/', views.template_detail, name='template_detail'),
    path('<int:template_id>/preview/', views.template_preview, name='template_preview'),
]