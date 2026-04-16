# import json
# import os
# import pika

# def publish_event(routing_key, payload):
#     print(f"🔥 Publishing {routing_key}: {payload}")  # ← ADD
#     host = os.getenv("RABBITMQ_HOST", "rabbitmq")
#     port = int(os.getenv("RABBITMQ_PORT", 5672))
    
    

#     credentials = pika.PlainCredentials("guest", "guest")
#     params = pika.ConnectionParameters(
#         host="rabbitmq",
#         port=5672,
#         virtual_host="/",
#         credentials=credentials,
#     )

import json
import os
import pika
from .circuit_breakers import rabbitmq_breaker

@rabbitmq_breaker
def publish_event(routing_key, payload):
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", 5672))

    credentials = pika.PlainCredentials("guest", "guest")
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        virtual_host="/",
        blocked_connection_timeout=5,
        socket_timeout=5,
        heartbeat=30
    )

    connection = pika.BlockingConnection(parameters)  # Let this raise original exception
    channel = connection.channel()

    channel.exchange_declare(
        exchange="todo_exchange",
        exchange_type="direct",
        durable=True
    )

    channel.basic_publish(
        exchange="todo_exchange",
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json"
        )
    )

    connection.close()
    return True