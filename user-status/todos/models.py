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
        db_table = 'user_todos'

    def __str__(self):
        return f"{self.title} ({self.status})"