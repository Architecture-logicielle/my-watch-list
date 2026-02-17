from django import forms
from django.forms import ModelForm
from .models import Task, Show

# ---------------------------------------------------------
# 🔵 ANCIEN FORMULAIRE (TO DO LIST)
# ---------------------------------------------------------
class TaskForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Add new task'})
    )

    class Meta:
        model = Task
        fields = '__all__'


# ---------------------------------------------------------
# 🔴 NOUVEAU FORMULAIRE (WATCHLIST)
# ---------------------------------------------------------
class ShowForm(forms.ModelForm):
    class Meta:
        model = Show
        fields = ['title', 'provider']
