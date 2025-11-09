from django.urls import path
from user_task import views

urlpatterns = [
    path("tasks", views.tasks, name="tasks"),
    path("tasks/<int:pk>", views.task, name="task"),
]
