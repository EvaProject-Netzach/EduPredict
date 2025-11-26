from django import forms
from .models import Ramo, Nota

class CrearRamoForm(forms.ModelForm):
    tiene_examen = forms.BooleanField(required=False, label="¿Tiene examen?")

    class Meta:
        model = Ramo
        fields = ["nombre", "tiene_examen"]


class NotaForm(forms.Form):
    nota = forms.FloatField(required=False, label="Nota")
    porcentaje = forms.FloatField(label="Porcentaje")
    es_examen = forms.BooleanField(required=False)
