from django import forms
from .models import Video, Tema
class VideoForm(forms.ModelForm):
    # La consulta de `Tema` debe realizarse al instanciar el formulario para
    # reflejar los temas creados después de que se cargó el módulo.
    temas = forms.ModelMultipleChoiceField(
        queryset=Tema.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'select2', 'multiple': 'multiple'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Al inicializar el formulario, actualizamos el queryset para que
        # incluya todos los temas disponibles en la base de datos.
        self.fields['temas'].queryset = Tema.objects.all()

    class Meta:
        model = Video  
        fields = ['nombre', 'temas', 'url_codigo']