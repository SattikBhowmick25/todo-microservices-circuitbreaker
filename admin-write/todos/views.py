# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import Todo
# from .serializers import TodoSerializer
# import pika
# import json
# from django.conf import settings
# from .producer import publish_event

# @api_view(['GET', 'POST'])
# def todo_list_create(request):
#     if request.method == 'GET':
#         todos = Todo.objects.all()
#         serializer = TodoSerializer(todos, many=True)
#         return Response(serializer.data)
    
#     elif request.method == 'POST':
#         serializer = TodoSerializer(data=request.data)
#         if serializer.is_valid():
#             todo = serializer.save()
#             # After todo.save()
#             print(f"🔥 Calling publish_event for todo ID={todo.id}")
#             try:
#                 publish_event("todo.created", {
#                     "todo_id": todo.id,
#                     "title": todo.title,
#                     "description": todo.description,
#                     "status": todo.status
#                 })
#                 print(f"✅ Published todo.created ID={todo.id}")
#             except Exception as e:
#                 print(f"❌ Producer failed: {e}")
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def todo_detail(request, pk):
#     try:
#         todo = Todo.objects.get(pk=pk)
#     except Todo.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = TodoSerializer(todo)
#         return Response(serializer.data)
    
#     elif request.method == 'PUT':
#         serializer = TodoSerializer(todo, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             # Publish event
#             publish_event('todo.updated', {
#                 'todo_id': todo.id,
#                 'title': todo.title,
#                 'description': todo.description,
#                 'status': todo.status,
#                 'updated_at': todo.updated_at.isoformat(),
#             })
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     elif request.method == 'DELETE':
#         todo.delete()
#         publish_event('todo.deleted', {'todo_id': pk})
#         return Response(status=status.HTTP_204_NO_CONTENT)

# def publish_event(event_type, payload):
#     """Publish event to RabbitMQ"""
#     try:
#         # FIXED - match consumer exchange
#         connection = pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@rabbitmq:5672/%2F'))
#         channel = connection.channel()
#         channel.exchange_declare(exchange='todo_exchange', exchange_type='direct', durable=True)  # ← FIXED

#         channel.basic_publish(
#             exchange='todo_exchange',  # ← FIXED
#             routing_key=event_type,
#             body=json.dumps(payload),
#             properties=pika.BasicProperties(delivery_mode=2),  # Persistent
#         )
#         connection.close()
#         print(f"✅ Published {event_type}")  # ← ADD
#     except Exception as e:
#         print(f"Failed to publish event {event_type}: {e}")

from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pybreaker

from .circuit_breakers import rabbitmq_breaker
from .models import Todo, OutboxEvent
from .producer import publish_event


@api_view(['GET', 'POST'])
def todo_list_create(request):
    if request.method == 'GET':
        todos = Todo.objects.all().order_by('-id').values()
        return Response(list(todos), status=status.HTTP_200_OK)

    if request.method == 'POST':
        title = request.data.get("title")
        description = request.data.get("description", "")
        todo_status = request.data.get("status", "pending")

        if not title:
            return Response(
                {"error": "title is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            todo = Todo.objects.create(
                title=title,
                description=description,
                status=todo_status
            )

            event_payload = {
                "todo_id": str(todo.external_id),
                "title": todo.title,
                "description": todo.description,
                "status": todo.status
            }

            outbox_event = OutboxEvent.objects.create(
                exchange="todo_exchange",
                routing_key="todo.created",
                payload=event_payload,
                status="pending",
                max_retries=5  
            )

        try:
            publish_event("todo.created", event_payload)
            outbox_event.status = "sent"
            outbox_event.sent_at = timezone.now()
            outbox_event.last_error = ""
            outbox_event.save(update_fields=["status", "sent_at", "last_error"])

            return Response(
                {
                    "message": "Todo created and event published successfully",
                    "todo": {
                        "id": todo.id,
                        "external_id": todo.external_id,
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                },
                status=status.HTTP_201_CREATED
            )

        except pybreaker.CircuitBreakerError:
            return Response(
                {
                    "message": "Todo created, but RabbitMQ circuit is open. Event saved for retry.",
                    "todo": {
                        "id": todo.id,
                        "external_id": todo.external_id,
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                },
                status=status.HTTP_202_ACCEPTED
            )

        except Exception as e:
            outbox_event.retry_count += 1
            outbox_event.last_error = str(e)
            outbox_event.status = "failed"
            outbox_event.save(update_fields=["retry_count", "last_error", "status"])

            return Response(
                {
                    "message": "Todo created, but event publish failed. Saved for retry.",
                    "error": str(e),
                    "todo": {
                        "id": todo.id,
                        "external_id": todo.external_id,
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                },
                status=status.HTTP_202_ACCEPTED
            )


@api_view(['GET', 'PUT', 'DELETE'])
def todo_detail(request, pk):
    try:
        todo = Todo.objects.get(pk=pk)
    except Todo.DoesNotExist:
        return Response(
            {"error": "Todo not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        return Response(
            {
                "id": todo.id,
                "external_id": todo.external_id,
                "title": todo.title,
                "description": todo.description,
                "status": todo.status
            },
            status=status.HTTP_200_OK
        )

    if request.method == 'PUT':
        todo.title = request.data.get("title", todo.title)
        todo.description = request.data.get("description", todo.description)
        todo.status = request.data.get("status", todo.status)
        todo.save()

        event_payload = {
            "todo_id": str(todo.external_id),
            "title": todo.title,
            "description": todo.description,
            "status": todo.status
        }

        outbox_event = OutboxEvent.objects.create(
            exchange="todo_exchange",
            routing_key="todo.updated",
            payload=event_payload,
            status="pending",
            max_retries=5  
        )

        try:
            publish_event("todo.updated", event_payload)
            outbox_event.status = "sent"
            outbox_event.sent_at = timezone.now()
            outbox_event.last_error = ""
            outbox_event.save(update_fields=["status", "sent_at", "last_error"])

        except pybreaker.CircuitBreakerError:
            pass

        except Exception as e:
            outbox_event.retry_count += 1
            outbox_event.last_error = str(e)
            outbox_event.status = "failed"
            outbox_event.save(update_fields=["retry_count", "last_error", "status"])

        return Response(
            {
                "message": "Todo updated successfully",
                "todo": {
                    "id": todo.id,
                    "external_id": todo.external_id,
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status
                }
            },
            status=status.HTTP_200_OK
        )

    if request.method == 'DELETE':
        event_payload = {
            "todo_id": str(todo.external_id)
        }

        outbox_event = OutboxEvent.objects.create(
            exchange="todo_exchange",
            routing_key="todo.deleted",
            payload=event_payload,
            status="pending",
            max_retries=5
        )

        todo.delete()

        try:
            publish_event("todo.deleted", event_payload)
            outbox_event.status = "sent"
            outbox_event.sent_at = timezone.now()
            outbox_event.last_error = ""
            outbox_event.save(update_fields=["status", "sent_at", "last_error"])

        except pybreaker.CircuitBreakerError:
            pass

        except Exception as e:
            outbox_event.retry_count += 1
            outbox_event.last_error = str(e)
            outbox_event.status = "failed"
            outbox_event.save(update_fields=["retry_count", "last_error", "status"])

        return Response(
            {"message": "Todo deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
def breaker_status(request):
    return Response(
        {
            "name": rabbitmq_breaker.name,
            "current_state": rabbitmq_breaker.current_state
        },
        status=status.HTTP_200_OK
    )