from django import forms
from .models import AlgorithmConfig, SavedConfiguration

HYPERPARAMETER_FIELDS = {
    'linear_regression': [],
    'ridge_regression': ['alpha'],
    'lasso_regression': ['alpha'],
    'random_forest': ['n_estimators', 'max_depth'],
    'gradient_boosting': ['n_estimators', 'learning_rate', 'max_depth'],
    'svm': ['C', 'kernel'],
    'neural_network': ['hidden_layers', 'max_iter'],
    'decision_tree': ['max_depth'],
    'knn': ['n_neighbors'],
    'naive_bayes': [],
}

class AlgorithmConfigForm(forms.ModelForm):
    # Common hyperparameters
    alpha = forms.FloatField(required=False, initial=1.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), label='Lambda (α)')
    n_estimators = forms.IntegerField(required=False, initial=100, widget=forms.NumberInput(attrs={'class': 'form-control'}), label='Number of Estimators')
    max_depth = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}), label='Max Depth (leave empty for unlimited)')
    learning_rate = forms.FloatField(required=False, initial=0.1, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    C = forms.FloatField(required=False, initial=1.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}), label='Regularization (C)')
    kernel = forms.ChoiceField(required=False, choices=[('rbf', 'RBF'), ('linear', 'Linear'), ('poly', 'Polynomial')], widget=forms.Select(attrs={'class': 'form-select'}))
    hidden_layers = forms.CharField(required=False, initial='100', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 100,50,25'}), label='Hidden Neurons (comma-separated)')
    max_iter = forms.IntegerField(required=False, initial=500, widget=forms.NumberInput(attrs={'class': 'form-control'}), label='Max Iterations')
    n_neighbors = forms.IntegerField(required=False, initial=5, widget=forms.NumberInput(attrs={'class': 'form-control'}), label='Number of Neighbors (k)')

    class Meta:
        model = AlgorithmConfig
        fields = ['name', 'algorithm_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'algorithm_type': forms.Select(attrs={'class': 'form-select', 'id': 'algorithm_type_select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        algo = instance.algorithm_type
        fields = HYPERPARAMETER_FIELDS.get(algo, [])
        hp = {}
        for field in fields:
            val = self.cleaned_data.get(field)
            if val is not None and val != '':
                hp[field] = val
        instance.hyperparameters = hp
        if commit:
            instance.save()
        return instance

class SavedConfigForm(forms.ModelForm):
    class Meta:
        model = SavedConfiguration
        fields = ['name', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class TrainModelForm(forms.Form):
    from datasets.models import Dataset
    dataset = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Dataset'
    )
    algorithm = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Algorithm'
    )
    target_column = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Target column name'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datasets.models import Dataset
        self.fields['dataset'].queryset = Dataset.objects.filter(status='active')
        self.fields['algorithm'].queryset = AlgorithmConfig.objects.filter(status='enabled')