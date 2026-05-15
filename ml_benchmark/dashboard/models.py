from django.db import models
from accounts.models import CustomUser
from datasets.models import Dataset
from algorithms.models import AlgorithmConfig

class BenchmarkJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    name = models.CharField(max_length=200)
    datasets = models.ManyToManyField(Dataset)
    algorithms = models.ManyToManyField(AlgorithmConfig)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Benchmark: {self.name}"