from rest_framework import serializers
from user_task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "parent", "subtasks"]

    def get_subtasks(self, obj):
        depth = self.context.get("depth", 1)
        if depth is None:
            return TaskSerializer(
                obj.get_children(), many=True, context=self.context
            ).data
        if depth <= 0:
            return []
        return TaskSerializer(
            obj.get_children(), many=True, context={**self.context, "depth": depth - 1}
        ).data
