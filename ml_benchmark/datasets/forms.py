from django import forms
from .models import Dataset

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'domain', 'task_type', 'description', 'file', 'version', 'target_column']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Iris Classification Dataset'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Healthcare, Finance'}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief dataset description'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls,.json'}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1.0'}),
            'target_column': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Target/label column name (for supervised learning)'}),
        }

class DatasetFilterForm(forms.Form):
    task_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Dataset.TASK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    domain = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by domain'})
    )