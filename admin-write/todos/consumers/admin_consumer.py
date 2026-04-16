# #!/usr/bin/env python
# import os
# import django
# import sys
# import pika
# import json
# from pathlib import Path

# # Setup Django
# sys.path.append(str(Path(__file__).parent.parent.parent))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_write.settings')
# django.setup()

# from todos.models import Todo

# RABBITMQ_URL = 'amqp://guest:guest@rabbitmq:5672//'

# def callback(ch, method, properties, body):
#     try:
#         data = json.loads(body)
#         event_type = method.routing_key
        
#         if event_type == 'todo.status_updated':
#             todo_id = data['todo_id']
#             status = data['status']
            
#             todo, created = Todo.objects.update_or_create(
#                 external_id=todo_id,
#                 defaults={'status': status}
#             )
#             print(f"Admin consumer: Updated todo {todo_id} status to {status}")
        
#         ch.basic_ack(delivery_tag=method.delivery_tag)
#     except Exception as e:
#         print(f"Admin consumer error: {e}")
#         ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# def main():
#     params = pika.URLParameters(RABBITMQ_URL)
#     connection = pika.BlockingConnection(params)
#     channel = connection.channel()
    
#     channel.exchange_declare(exchange='todo_events', exchange_type='direct', durable=True)
#     result = channel.queue_declare(queue='admin_status_queue', durable=True)
#     queue_name = result.method.queue
    
#     channel.queue_bind(
#         exchange='todo_events',
#         queue=queue_name,
#         routing_key='todo.status_updated'
#     )
    
#     channel.basic_qos(prefetch_count=1)
#     channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
#     print('Admin consumer started. Waiting for status updates...')
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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_write.settings')
django.setup()
from todos.models import Todo

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        todo_id = data.get("todo_id")
        status_value = data.get("status")

        if not todo_id or not status_value:
            print("Invalid message payload:", data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        todo = Todo.objects.get(id=todo_id)
        todo.status = status_value
        todo.save()

        print(f"Updated admin todo {todo_id} to status={status_value}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Todo.DoesNotExist:
        print(f"Todo with id={data.get('todo_id')} not found in admin-write DB")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Consumer error:", str(e))
        ch.basic_ack(delivery_tag=method.delivery_tag)

host = os.getenv("RABBITMQ_HOST", "rabbitmq")
port = int(os.getenv("RABBITMQ_PORT", 5672))

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host, port=port)
)
channel = connection.channel()

channel.exchange_declare(
    exchange="todo_exchange",
    exchange_type="direct",
    durable=True
)

channel.queue_declare(queue="admin_todo_status_queue", durable=True)

channel.queue_bind(
    exchange="todo_exchange",
    queue="admin_todo_status_queue",
    routing_key="todo.status_updated"
)

channel.basic_qos(prefetch_count=1)

channel.basic_consume(
    queue="admin_todo_status_queue",
    on_message_callback=callback,
    auto_ack=False
)

print("Admin consumer is waiting for todo.status_updated messages...")
channel.start_consuming()