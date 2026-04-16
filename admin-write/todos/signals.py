from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Todo
from .producer import publish_event  # your producer file

@receiver(post_save, sender=Todo)
def publish_todo_created(sender, instance, created, **kwargs):
    if created:
        print(f"🔥 Calling publish_event for todo ID={instance.id}")
        try:
            publish_event("todo.created", {
                "todo_id": instance.id,
                "title": instance.title,
                "description": instance.description,
                "status": instance.status
            })
            print(f"✅ Published todo.created ID={instance.id}")
        except Exception as e:
            print(f"❌ Producer failed: {e}")