from django.urls import path
from . import views

urlpatterns = [
    path('todos/', views.todo_list_status, name='todo-list-status'),
    path("todos/<int:todo_id>/status/", views.update_todo_status, name="update_todo_status"),
]