from rest_framework import serializers
from .models import Todo

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'external_id', 'title', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']