# import json
# import os
# import pika

# def publish_event(routing_key, payload):
#     host = os.getenv("RABBITMQ_HOST", "rabbitmq")
#     port = int(os.getenv("RABBITMQ_PORT", 5672))

#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host=host, port=port)
#     )
#     channel = connection.channel()

#     channel.exchange_declare(
#         exchange="todo_exchange",
#         exchange_type="direct",
#         durable=True
#     )

#     channel.basic_publish(
#         exchange="todo_exchange",
#         routing_key=routing_key,
#         body=json.dumps(payload),
#         properties=pika.BasicProperties(
#             delivery_mode=2,
#             content_type="application/json"
#         )
#     )

#     connection.close()

import json
import os
import pika

def publish_event(routing_key, payload):
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", 5672))
    
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host=host, 
        port=port,
        credentials=credentials,
        virtual_host='/'
    )

    connection = pika.BlockingConnection(parameters)
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