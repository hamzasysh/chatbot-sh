# forms.py
from django import forms
from .models import TrainingFile

class TrainingForm(forms.ModelForm):
    class Meta:
        model = TrainingFile
        fields = ['file']
