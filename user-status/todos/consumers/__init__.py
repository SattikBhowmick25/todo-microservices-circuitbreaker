def run_user_consumer():
    """User consumer - listens for todo.created"""
    import os, sys, json, pika, django
    
    sys.path.insert(0, "/app")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_status.settings")
    django.setup()
    
    from todos.models import Todo
    
    def callback(ch, method, properties, body):
        data = json.loads(body)
        todo, created = Todo.objects.update_or_create(
            external_id=data['todo_id'],
            defaults={'title': data['title'], 'description': data['description'], 'status': data['status']}
        )
        print(f"✅ User synced todo {data['todo_id']} ({'created' if created else 'updated'})")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
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
    # result = channel.queue_declare(queue="user_todo_queue", durable=True)
    result = channel.queue_declare(
        queue="user_todo_queue",
        durable=True
    )
    channel.queue_bind(exchange="todo_exchange", queue=result.method.queue, routing_key="todo.created")
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=result.method.queue, on_message_callback=callback)
    print("🎾 User consumer ready for todo.created...")
    channel.start_consuming()