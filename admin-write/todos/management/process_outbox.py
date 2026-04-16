from django.core.management.base import BaseCommand
from django.utils import timezone
import pybreaker

from todos.models import OutboxEvent
from todos.producer import publish_event

class Command(BaseCommand):
    help = "Process pending outbox events"

    def handle(self, *args, **kwargs):
        events = OutboxEvent.objects.filter(status__in=["pending", "failed"]).order_by("created_at")[:50]

        if not events.exists():
            self.stdout.write(self.style.SUCCESS("No outbox events to process"))
            return

        for event in events:
            try:
                publish_event(event.routing_key, event.payload)
                event.status = "sent"
                event.sent_at = timezone.now()
                event.last_error = ""
                event.save(update_fields=["status", "sent_at", "last_error"])
                self.stdout.write(self.style.SUCCESS(f"Sent event {event.id}"))

            except pybreaker.CircuitBreakerError:
                self.stdout.write(self.style.WARNING(
                    f"Circuit breaker open. Stopping retry loop at event {event.id}"
                ))
                break

            except Exception as e:
                event.retry_count += 1
                event.status = "failed"
                event.last_error = str(e)
                event.save(update_fields=["retry_count", "status", "last_error"])
                self.stdout.write(self.style.ERROR(f"Failed event {event.id}: {e}"))