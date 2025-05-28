from django import forms
from .models import Video, Tema
class VideoForm(forms.ModelForm):
    temas = forms.ModelMultipleChoiceField(
        queryset=Tema.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2', 'multiple': 'multiple'}),
        required=False
    )

    class Meta:
        model = Video  
        fields = ['nombre', 'temas', 'url_codigo']