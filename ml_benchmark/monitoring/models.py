from django.db import models

class ModuleHealth(models.Model):
    MODULE_CHOICES = [
        ('datasets', 'Dataset Module'),
        ('algorithms', 'Algorithm Module'),
        ('diagnostics', 'Diagnostics Module'),
        ('dashboard', 'Dashboard Module'),
        ('exports', 'Exports Module'),
        ('database', 'Database'),
        ('storage', 'File Storage'),
    ]
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('unknown', 'Unknown'),
    ]
    module_name = models.CharField(max_length=50, choices=MODULE_CHOICES, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    response_time = models.FloatField(null=True, blank=True)
    message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.module_name}: {self.status}"

class SystemAlert(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    module = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.module}: {self.message[:50]}"