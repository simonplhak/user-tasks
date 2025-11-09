from django.db import models
from django.contrib.auth.models import User
from mptt import models as mptt_models


class Task(mptt_models.MPTTModel):
    class MPTTMeta:
        order_insertion_by = ["created_at"]

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    parent = mptt_models.TreeForeignKey(
        "self", on_delete=models.CASCADE, related_name="subtasks", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
