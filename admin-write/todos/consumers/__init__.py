def run_admin_consumer():
    import json, pika, django, os, sys
    sys.path.insert(0, "/app")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_write.settings")
    django.setup()
    from todos.models import Todo
    
    # params = pika.ConnectionParameters('rabbitmq', virtual_host='/')
    params = pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('guest', 'guest'),
        heartbeat=60,
        blocked_connection_timeout=100,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    # CORRECT - must match producer
    channel.exchange_declare(
        exchange="todo_exchange", 
        exchange_type="direct",
        durable=True  # ← ADD THIS
    )
    # result = channel.queue_declare(queue="admin_status_queue")
    result = channel.queue_declare(
        queue="admin_status_queue",
        durable=True
    )
    channel.queue_bind(exchange="todo_exchange", queue=result.method.queue, routing_key="todo.status_updated")
    
    def callback(ch, method, properties, body):
        data = json.loads(body)
        todo = Todo.objects.get(external_id=data['todo_id'])
        todo.status = data['status']
        todo.save()
        print(f"Admin updated {data['todo_id']} -> {data['status']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(queue=result.method.queue, on_message_callback=callback)
    print("Admin consumer ready")
    channel.start_consuming()