from django.shortcuts import get_object_or_404
from django.db.transaction import atomic
import mptt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from user_task.models import Task
from user_task.serializers import TaskSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@atomic
def tasks(request: Request) -> Response:
    serializer = TaskSerializer(data=request.data)
    if request.method == "GET":
        filter_kwargs = {"user": request.user, "parent": None}
        if status := request.query_params.get("status"):
            status = status.upper()
            print(
                type(Task.Status.choices), type(Task.Status.values), Task.Status.values
            )
            if status not in Task.Status.values:
                raise ValidationError(
                    detail=f"Allowed status queries: {Task.Status.values}"
                )
            filter_kwargs["status"] = status
        if title := request.query_params.get("title"):
            title = title
            filter_kwargs["title__icontains"] = title
        tasks = Task.objects.filter(**filter_kwargs)
        serializer = TaskSerializer(tasks, many=True, context={"depth": 0})
        return Response(serializer.data)
    if request.method == "POST":
        if not serializer.is_valid():
            raise ValidationError()
        try:
            serializer.save(user=request.user)
        except Exception as e:
            raise ValidationError(detail=f"Error during task creation: {str(e)}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    raise MethodNotAllowed(request.method)


@api_view(["GET", "DELETE", "PUT"])
@permission_classes([IsAuthenticated])
@atomic
def task(request: Request, pk: int) -> Response:
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "GET":
        depth = 1
        if request.query_params.get("full", "0") == "1":
            depth = None
        elif _depth := request.query_params.get("depth"):
            depth = _depth
        serializer = TaskSerializer(task, context={"depth": depth})
        return Response(serializer.data)
    if request.method == "DELETE":
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == "PUT":
        serializer = TaskSerializer(
            task, data=request.data, context={"depth": 1}, partial=True
        )
        if not serializer.is_valid():
            raise ValidationError()
        try:
            serializer.save(user=request.user)
        except mptt.exceptions.InvalidMove:
            raise ValidationError(detail="Task cannot be its own ancestor.")
        return Response(serializer.data)
    raise MethodNotAllowed(request.method)
