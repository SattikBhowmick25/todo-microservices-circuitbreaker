from django.db import models

class Todo(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.IntegerField(null=True, blank=True, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_todos'

    def __str__(self):
        return f"{self.title} ({self.status})"
    
# class OutboxEvent(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('sent', 'Sent'),
#         ('failed', 'Failed'),
#     ]

#     exchange = models.CharField(max_length=100)
#     routing_key = models.CharField(max_length=100)
#     payload = models.JSONField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     retry_count = models.PositiveIntegerField(default=0)
#     last_error = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     sent_at = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.routing_key} - {self.status}"

class OutboxEvent(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_DEAD_LETTERED = 'dead_lettered'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_DEAD_LETTERED, 'Dead Lettered'),
    ]
    
    id = models.AutoField(primary_key=True)
    exchange = models.CharField(max_length=255)
    routing_key = models.CharField(max_length=255)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=5)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        
    def __str__(self):
        return f"Event {self.id}: {self.routing_key} [{self.status}]"