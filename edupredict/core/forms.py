from django import forms
from .models import Ramo, Nota

class CrearRamoForm(forms.ModelForm): #form para ver si tiene examen o no
    tiene_examen = forms.BooleanField(required=False, label="¿Tiene examen?")

    class Meta:
        model = Ramo
        fields = ["nombre", "tiene_examen"]


class NotaForm(forms.Form): # notas
    nota = forms.FloatField(required=False, label="Nota")
    porcentaje = forms.FloatField(label="Porcentaje")
    es_examen = forms.BooleanField(required=False)
