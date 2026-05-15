from django.db import models
from datasets.models import Dataset
from accounts.models import CustomUser

class DiagnosticReport(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='diagnostics')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    vif_results = models.JSONField(default=dict)
    high_vif_features = models.JSONField(default=list)
    vif_threshold = models.FloatField(default=5.0)
    correlation_matrix = models.JSONField(default=dict)
    heatmap_image = models.ImageField(upload_to='diagnostics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Diagnostic for {self.dataset.name}"