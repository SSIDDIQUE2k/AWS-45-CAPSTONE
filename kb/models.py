from django.db import models
import json


class Document(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=64, default='local')  # 'local' | 'external'
    uri = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.source})"


class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    text = models.TextField()
    # Store embedding as JSON string for SQLite compatibility
    embedding = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['document', 'order']),
        ]

    def set_embedding(self, embedding_vector):
        """Store embedding as JSON string"""
        if embedding_vector is not None:
            self.embedding = json.dumps(embedding_vector.tolist() if hasattr(embedding_vector, 'tolist') else embedding_vector)
        else:
            self.embedding = None

    def get_embedding(self):
        """Retrieve embedding as list"""
        if self.embedding:
            return json.loads(self.embedding)
        return None

