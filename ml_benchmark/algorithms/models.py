from django.db import models
from accounts.models import CustomUser

class AlgorithmConfig(models.Model):
    ALGORITHM_CHOICES = [
        ('linear_regression', 'Linear Regression'),
        ('ridge_regression', 'Ridge Regression'),
        ('lasso_regression', 'Lasso Regression'),
        ('random_forest', 'Random Forest'),
        ('gradient_boosting', 'Gradient Boosting'),
        ('svm', 'Support Vector Machine'),
        ('neural_network', 'Neural Network (MLP)'),
        ('decision_tree', 'Decision Tree'),
        ('knn', 'K-Nearest Neighbors'),
        ('naive_bayes', 'Naive Bayes'),
    ]
    STATUS_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
        ('testing', 'Testing'),
    ]
    name = models.CharField(max_length=100)
    algorithm_type = models.CharField(max_length=50, choices=ALGORITHM_CHOICES)
    description = models.TextField(blank=True)
    hyperparameters = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enabled')
    is_admin_configured = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_algorithm_type_display()})"

class SavedConfiguration(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    algorithm_config = models.ForeignKey(AlgorithmConfig, on_delete=models.CASCADE)
    dataset_id = models.IntegerField(null=True, blank=True)
    hyperparameters = models.JSONField(default=dict)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"

class TrainingResult(models.Model):
    dataset = models.ForeignKey('datasets.Dataset', on_delete=models.CASCADE)
    algorithm_config = models.ForeignKey(AlgorithmConfig, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rmse = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    r2_score = models.FloatField(null=True, blank=True)
    cv_scores = models.JSONField(default=list)
    training_time = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='completed')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.algorithm_config.name} on {self.dataset.name}"