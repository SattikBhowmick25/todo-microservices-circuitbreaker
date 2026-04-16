from django.urls import path
from . import views

urlpatterns = [
    path('todos/', views.todo_list_create, name='todo-list-create'),
    path('todos/<int:pk>/', views.todo_detail, name='todo-detail'),
    path('breaker-status/', views.breaker_status, name='breaker-status'),
]