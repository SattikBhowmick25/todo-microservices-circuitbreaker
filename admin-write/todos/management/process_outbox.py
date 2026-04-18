# from django.core.management.base import BaseCommand
# from django.utils import timezone
# import pybreaker

# from todos.models import OutboxEvent
# from todos.producer import publish_event

# class Command(BaseCommand):
#     help = "Process pending outbox events"

#     def handle(self, *args, **kwargs):
#         events = OutboxEvent.objects.filter(status__in=["pending", "failed"]).order_by("created_at")[:50]

#         if not events.exists():
#             self.stdout.write(self.style.SUCCESS("No outbox events to process"))
#             return

#         for event in events:
#             try:
#                 publish_event(event.routing_key, event.payload)
#                 event.status = "sent"
#                 event.sent_at = timezone.now()
#                 event.last_error = ""
#                 event.save(update_fields=["status", "sent_at", "last_error"])
#                 self.stdout.write(self.style.SUCCESS(f"Sent event {event.id}"))

#             except pybreaker.CircuitBreakerError:
#                 self.stdout.write(self.style.WARNING(
#                     f"Circuit breaker open. Stopping retry loop at event {event.id}"
#                 ))
#                 break

#             except Exception as e:
#                 event.retry_count += 1
#                 event.status = "failed"
#                 event.last_error = str(e)
#                 event.save(update_fields=["retry_count", "status", "last_error"])
#                 self.stdout.write(self.style.ERROR(f"Failed event {event.id}: {e}"))

import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from todos.models import OutboxEvent
from todos.producer import publish_event
import models

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process outbox events with retry logic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of events to process per batch'
        )
        parser.add_argument(
            '--max-runtime',
            type=int,
            default=300,  # 5 minutes
            help='Max runtime in seconds'
        )
        parser.add_argument(
            '--poll-interval',
            type=float,
            default=5.0,
            help='Seconds between polling cycles'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        max_runtime = options['max_runtime']
        poll_interval = options['poll_interval']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting outbox worker: batch_size={batch_size}, '
                f'max_runtime={max_runtime}s, poll_interval={poll_interval}s'
            )
        )

        start_time = time.time()
        processed = 0
        failed = 0

        while time.time() - start_time < max_runtime:
            try:
                count = self.process_batch(batch_size)
                processed += count
                self.stdout.write(f'Processed {count} events (total: {processed})')
                
                if count == 0:
                    self.stdout.write('No events to process, sleeping...')
                    time.sleep(poll_interval)
                    
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Interrupted by user'))
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(poll_interval)

        self.stdout.write(
            self.style.SUCCESS(
                f'Worker stopped. Processed: {processed}, Failed: {failed}'
            )
        )

    @transaction.atomic
    def process_batch(self, batch_size):
        # Get eligible events: pending OR failed with expired retry timeout
        now = timezone.now()
        
        events = OutboxEvent.objects.filter(
            models.Q(status='pending') |
            models.Q(
                status='failed',
                next_retry_at__lte=now,
                max_retries__gt=models.F('retry_count')
            )
        ).select_for_update(skip_locked=True)[:batch_size]

        if not events.exists():
            return 0

        success_count = 0
        for event in events:
            try:
                self.process_single_event(event)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process event {event.id}: {e}")
                continue

        return success_count

    def process_single_event(self, event):
        # Calculate backoff delay
        backoff_delay = self.calculate_backoff(event.retry_count)
        
        try:
            publish_event(event.routing_key, event.payload)
            
            # Mark as sent
            event.status = 'sent'
            event.sent_at = timezone.now()
            event.last_error = ''
            event.save(update_fields=['status', 'sent_at', 'last_error'])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Event {event.id} sent: {event.routing_key} '
                    f'(retry #{event.retry_count})'
                )
            )
            
        except Exception as e:
            # Schedule retry
            event.retry_count += 1
            event.last_error = str(e)
            event.next_retry_at = timezone.now() + timezone.timedelta(seconds=backoff_delay)
            
            if event.retry_count >= getattr(event, 'max_retries', 5):
                event.status = 'dead_lettered'
                self.stdout.write(
                    self.style.ERROR(
                        f'💀 Event {event.id} dead lettered (max retries exceeded)'
                    )
                )
            else:
                event.status = 'failed'
                self.stdout.write(
                    self.style.WARNING(
                        f'🔄 Event {event.id} failed (#{event.retry_count}), '
                        f'next retry in {backoff_delay}s'
                    )
                )
            
            event.save(update_fields=[
                'retry_count', 'last_error', 'next_retry_at', 'status'
            ])

    def calculate_backoff(self, retry_count):
        """Exponential backoff with jitter: 1s, 3s, 10s, 30s, 60s..."""
        base_delay = min(60 * (2 ** retry_count), 300)  # Cap at 5min
        jitter = base_delay * 0.1 * (hash(str(retry_count)) % 1000 / 1000)
        return base_delay + jitter