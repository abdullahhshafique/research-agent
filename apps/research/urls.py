"""
Research app URL patterns.
"""
from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    path('', views.research_submit, name='research_submit'),
    path('<int:pk>/', views.research_status, name='research_status'),
    path('<int:pk>/stream/', views.research_stream, name='research_stream'),
    path('<int:pk>/retry/', views.research_retry, name='research_retry'),
    path('<int:pk>/version/', views.create_version, name='create_version'),
    path('<int:query_id>/cancel/', views.research_cancel, name='research_cancel'),
]