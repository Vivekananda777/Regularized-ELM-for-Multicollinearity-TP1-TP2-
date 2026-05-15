from django.db import models
from accounts.models import CustomUser


class Dataset(models.Model):
    TASK_CHOICES = [
        ('classification', 'Classification'),
        ('regression', 'Regression'),
        ('clustering', 'Clustering'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('processing', 'Processing'),
    ]
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=100)
    task_type = models.CharField(max_length=20, choices=TASK_CHOICES)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='datasets/')
    file_format = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    version = models.CharField(max_length=20, default='1.0')
    rows = models.IntegerField(null=True, blank=True)
    columns = models.IntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target_column = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"


class PreprocessingReport(models.Model):
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='preprocessing_report')
    missing_values_handled = models.IntegerField(default=0)
    columns_normalized = models.TextField(blank=True)
    columns_encoded = models.TextField(blank=True)
    outliers_removed = models.IntegerField(default=0)
    transformations = models.JSONField(default=dict)
    feature_names = models.JSONField(default=list)
    original_rows = models.IntegerField(default=0)
    original_cols = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.dataset.name}"