"""
History app URL patterns.
"""
from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.history_list, name='history_list'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/delete/', views.delete_history, name='delete_history'),
    path('bulk-delete/', views.bulk_delete_history, name='bulk_delete_history'),
    path('<int:pk>/save-template/', views.save_as_template, name='save_as_template'),
]