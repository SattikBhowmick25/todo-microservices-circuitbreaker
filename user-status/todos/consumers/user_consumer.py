# #!/usr/bin/env python
# import os
# import django
# import sys
# import pika
# import json
# from pathlib import Path

# # Setup Django
# sys.path.append(str(Path(__file__).parent.parent.parent))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_status.settings')
# django.setup()

# from todos.models import Todo

# RABBITMQ_URL = 'amqp://guest:guest@rabbitmq:5672//'

# def callback(ch, method, properties, body):
#     try:
#         data = json.loads(body)
#         event_type = method.routing_key
        
#         if event_type == 'todo.created':
#             todo_id = data['todo_id']
#             title = data['title']
#             description = data['description']
#             status = data['status']
            
#             todo = Todo.objects.create(
#                 external_id=todo_id,
#                 title=title,
#                 description=description,
#                 status=status
#             )
#             print(f"User consumer: Created todo {todo_id}: {title}")
        
#         elif event_type == 'todo.updated':
#             todo_id = data['todo_id']
#             title = data['title']
#             description = data['description']
#             status = data['status']
            
#             todo = Todo.objects.update_or_create(
#                 external_id=todo_id,
#                 defaults={
#                     'title': title,
#                     'description': description,
#                     'status': status
#                 }
#             )[0]
#             print(f"User consumer: Updated todo {todo_id}")
        
#         elif event_type == 'todo.deleted':
#             todo_id = data['todo_id']
#             Todo.objects.filter(external_id=todo_id).delete()
#             print(f"User consumer: Deleted todo {todo_id}")
        
#         ch.basic_ack(delivery_tag=method.delivery_tag)
#     except Exception as e:
#         print(f"User consumer error: {e}")
#         ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# def main():
#     params = pika.URLParameters(RABBITMQ_URL)
#     connection = pika.BlockingConnection(params)
#     channel = connection.channel()
    
#     channel.exchange_declare(exchange='todo_events', exchange_type='direct', durable=True)
#     result = channel.queue_declare(queue='user_todo_queue', durable=True)
#     queue_name = result.method.queue
    
#     channel.queue_bind(exchange='todo_events', queue=queue_name, routing_key='todo.created')
#     channel.queue_bind(exchange='todo_events', queue=queue_name, routing_key='todo.updated')
#     channel.queue_bind(exchange='todo_events', queue=queue_name, routing_key='todo.deleted')
    
#     channel.basic_qos(prefetch_count=1)
#     channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
#     print('User consumer started. Waiting for todo events...')
#     channel.start_consuming()

# if __name__ == '__main__':
#     main()

import os
import json
import django
import pika
import sys


# Fix Docker path issue  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_status.settings')
django.setup()

from todos.models import Todo

def callback(ch, method, properties, body):
    data = json.loads(body)

    Todo.objects.update_or_create(
        external_id=data["todo_id"],
        defaults={
            "title": data["title"],
            "description": data["description"],
            "status": data["status"],
        }
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)

host = os.getenv("RABBITMQ_HOST", "rabbitmq")
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = connection.channel()

channel.exchange_declare(exchange="todo_exchange", exchange_type="direct", durable=True)
channel.queue_declare(queue="user_todo_created", durable=True)
channel.queue_bind(exchange="todo_exchange", queue="user_todo_created", routing_key="todo.created")

channel.basic_consume(queue="user_todo_created", on_message_callback=callback)
channel.start_consuming()