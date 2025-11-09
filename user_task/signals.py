from rest_framework.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from user_task.models import Task


@receiver(pre_save, sender=Task)
def check_subtasks_done(sender, instance: Task, **kwargs):
    if instance.status != Task.Status.DONE:
        return
    # there is no need to check all descendants, if descendant is DONE, then all of its descendats must be DONE
    subtasks = instance.get_children()
    incomplete_subtasks = subtasks.exclude(status=Task.Status.DONE)

    if incomplete_subtasks.exists():
        raise ValidationError(
            detail="Cannot mark this task as DONE until all subtasks are DONE."
        )


@receiver(post_save, sender=Task)
def check_parent_undone(sender, instance: Task, **kwargs):
    if instance.status == Task.Status.DONE or instance.parent is None:
        return
    parent = instance.parent
    # propagate status from child node
    if parent.status != instance.status:
        return
    parent.status = Task.Status.IN_PROGRESS
    # this triggers recursion upwards, so all ancestors gets updated
    parent.save()
