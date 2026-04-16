from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Todo
from .serializers import TodoSerializer
import pika
import json
from django.conf import settings
from rest_framework import status as drf_status
from .producer import publish_event

@api_view(['GET', 'PATCH'])
def todo_list_status(request):
    if request.method == 'GET':
        todos = Todo.objects.all()
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Bulk status update
        todo_ids = request.data.get('todo_ids', [])
        new_status = request.data.get('status')
        
        if not todo_ids or not new_status:
            return Response({'error': 'todo_ids and status required'}, status=status.HTTP_400_BAD_REQUEST)
        
        updated = Todo.objects.filter(id__in=todo_ids).update(status=new_status)
        
        if updated > 0:
            # Publish event for all updated todos
            for todo in Todo.objects.filter(id__in=todo_ids):
                publish_event('todo.status_updated', {
                    'todo_id': todo.external_id,
                    'status': todo.status,
                    'updated_at': todo.updated_at.isoformat(),
                })
            return Response({'updated': updated})
        
        return Response({'updated': 0}, status=status.HTTP_200_OK)

def publish_event(event_type, payload):
    """Publish event to RabbitMQ"""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()
        channel.exchange_declare(exchange='todo_events', exchange_type='direct', durable=True)
        
        channel.basic_publish(
            exchange='todo_events',
            routing_key=event_type,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
    except Exception as e:
        print(f"Failed to publish event {event_type}: {e}")



@api_view(["PATCH"])
def update_todo_status(request, todo_id):
    try:
        todo = Todo.objects.get(pk=todo_id)
    except Todo.DoesNotExist:
        return Response({"error": "Todo not found"}, status=404)

    new_status = request.data.get("status")
    if not new_status:
        return Response({"error": "status is required"}, status=400)

    todo.status = new_status
    todo.save()

    publish_event("todo.status_updated", {
        "todo_id": todo.external_id,
        "status": todo.status
    })

    return Response({
        "message": "Todo status updated successfully",
        "todo_id": todo.id,
        "external_id": todo.external_id,
        "status": todo.status
    }, status=200)