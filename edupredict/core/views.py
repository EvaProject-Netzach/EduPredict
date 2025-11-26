from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Ramo
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import get_object_or_404


def index(request):
    return render(request, "index.html")

def calculadora_sin_registro(request):
    return render(request, "calculadora_sin_registro.html")



def registro(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("/login")

    return render(request, "registro.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            login(request, user)
            return redirect("/miperfil")
        else:
            return render(request, "login.html", {"error": "Credenciales incorrectas"})

    return render(request, "login.html")

def miperfil(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    return render(request, "miperfil.html")

class RamoForm(forms.ModelForm):
    class Meta:
        model = Ramo
        fields = ["nombre", "notas", "examen"]
        widgets = {
            "notas": forms.TextInput(attrs={"placeholder": "Separar notas con comas"}),
            "examen": forms.NumberInput(attrs={"step": 0.1}),
        }

@login_required
def crear_ramo(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        notas = []
        for key in request.POST:
            if key.startswith("nota_"):
                idx = key.split("_")[1]
                valor = request.POST.get(key)
                porc = request.POST.get(f"porc_{idx}", 0)
                notas.append({
                    "nota": float(valor) if valor else None,
                    "porcentaje": float(porc) if porc else 0
                })
        examen = {}
        if "examen_nota" in request.POST and request.POST.get("examen_nota"):
            examen = {
                "nota": float(request.POST.get("examen_nota")),
                "porcentaje": float(request.POST.get("examen_porcentaje") or 0)
            }

        Ramo.objects.create(user=request.user, nombre=nombre, notas=notas, examen=examen)
        return redirect("/mi-semestre")

    return render(request, "crear_ramo.html")

@login_required
def eliminar_ramo(request, ramo_id):
    try:
        ramo = Ramo.objects.get(id=ramo_id, user=request.user)
        ramo.delete()
    except Ramo.DoesNotExist:
        pass
    return redirect("/mi-semestre")

@login_required
def editar_ramo(request, ramo_id):
    ramo = get_object_or_404(Ramo, id=ramo_id, user=request.user)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        notas = []
        for key in request.POST:
            if key.startswith("nota_"):
                idx = key.split("_")[1]
                valor = request.POST.get(key)
                porc = request.POST.get(f"porc_{idx}", 0)
                notas.append({
                    "nota": float(valor) if valor else None,
                    "porcentaje": float(porc) if porc else 0
                })
        examen = {}
        if "examen_nota" in request.POST and request.POST.get("examen_nota"):
            examen = {
                "nota": float(request.POST.get("examen_nota")),
                "porcentaje": float(request.POST.get("examen_porcentaje") or 0)
            }

        ramo.nombre = nombre
        ramo.notas = notas
        ramo.examen = examen
        ramo.save()
        return redirect("/mi-semestre")

    return render(request, "crear_ramo.html", {"ramo": ramo})




@login_required
def mi_semestre(request):
    ramos = Ramo.objects.filter(user=request.user)
    return render(request, "mi_semestre.html", {"ramos": ramos})

def logout_view(request):
    logout(request)
    return redirect("/")
