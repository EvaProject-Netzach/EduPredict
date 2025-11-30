from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from rest_framework.reverse import reverse_lazy
from reservasAPP.models import *
from reservasAPP.serializers import ReservaSerializer
from rest_framework.response import Response
from rest_framework import status
from reservasAPP.forms import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Ramo, Semestre
from django.contrib.auth.models import User
from django.http import JsonResponse


# Create your views here.

@login_required
def mi_semestre(request):
    semestres = Semestre.objects.filter(user=request.user)
    semestre_actual_id = request.GET.get('semestre')
    
    if semestre_actual_id:
        semestre_actual = get_object_or_404(Semestre, id=semestre_actual_id, user=request.user)
        ramos = Ramo.objects.filter(user=request.user, semestre=semestre_actual)
    else:
        semestre_actual = semestres.first()
        ramos = Ramo.objects.filter(user=request.user, semestre=semestre_actual) if semestre_actual else []
    
    return render(request, "mi_semestre.html", {
        "ramos": ramos,
        "semestres": semestres,
        "semestre_actual": semestre_actual
    })

@login_required
def crear_semestres(request):
    if request.method == "POST":
        cantidad = int(request.POST.get("cantidad_semestres", 0))
        
        if cantidad > 0 and cantidad <= 8:
            # Eliminar semestres existentes del usuario
            Semestre.objects.filter(user=request.user).delete()
            
            # Crear nuevos semestres
            for i in range(1, cantidad + 1):
                Semestre.objects.create(
                    user=request.user,
                    nombre=f"{i}° Semestre",
                    orden=i
                )
            
            # Redirigir al primer semestre
            primer_semestre = Semestre.objects.filter(user=request.user).first()
            if primer_semestre:
                return redirect(f"/mi_semestre/?semestre={primer_semestre.id}")
    
    return redirect("miSemestre")

@login_required
def index(request):
    return render(request, "index.html")

class SignUpView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    success_message = "¡Usuario creado exitosamente!"

def reservasData(request):
    reservas = Reserva.objects.all()
    data = {'reservas': reservas}
    return render(request, 'reservas.html', data)


def registroReservas(request):
    form = ReservaForm()
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('reservas'))
            
    data = {'form': form}  
    return render(request, 'registroReservas.html', data)


def eliminarReservas(request, id):
    reserva = Reserva.objects.get(id=id)
    reserva.delete()
    return HttpResponseRedirect(reverse('reservas'))


def editarReservas(request, id):
    reserva = Reserva.objects.get(id=id)
    form = ReservaForm(instance=reserva)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('reservas'))
            
    data = {'form': form}  
    return render(request, 'registroReservas.html', data)




def estadosData(request):
    estados = Estado.objects.all()
    data = {'estados': estados}
    return render(request, 'estados.html', data)


def registroEstados(request):
    form = EstadoForm()
    
    if request.method == 'POST':
        form = EstadoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('estados'))
            
    data = {'form': form}  
    return render(request, 'registroEstados.html', data)


def eliminarEstados(request, id):
    estado = Estado.objects.get(id=id)
    estado.delete()
    return HttpResponseRedirect(reverse('estados'))


def editarEstados(request, id):
    estado = Estado.objects.get(id=id)
    form = EstadoForm(instance=estado)
    
    if request.method == 'POST':
        form = EstadoForm(request.POST, instance=estado)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('estados'))
            
    data = {'form': form}  
    return render(request, 'registroEstados.html', data)





@api_view(['GET', 'POST'])
def lista_reservas(request):
    if request.method == 'GET':
        reservas = Reserva.objects.all().order_by('fecha') # Muestra reservas orenadas por fecha
        serializer = ReservaSerializer(reservas, many=True) 
        return Response(serializer.data) 
    
    elif request.method == 'POST':
        serializer = ReservaSerializer(data=request.data) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    


@api_view(['GET', 'PUT', 'DELETE'])
def detalle_reservas(request, pk):
    try:
        reserva = Reserva.objects.get(pk=pk) 
    except Reserva.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ReservaSerializer(reserva) 
        return Response(serializer.data) 
    
    if request.method == 'PUT':
        serializer = ReservaSerializer(reserva, data=request.data) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    if request.method == 'DELETE':
        reserva.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


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
    semestres = Semestre.objects.filter(user=request.user)
    
    if not semestres.exists():
        return redirect("miSemestre")
    
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        semestre_id = request.POST.get("semestre")
        
        if not semestre_id:
            return redirect("crearRamo")
            
        semestre = get_object_or_404(Semestre, id=semestre_id, user=request.user)
        
        notas = []
        for key in request.POST:
            if key.startswith("nota_"):
                idx = key.split("_")[1]
                valor = request.POST.get(key)
                porc = request.POST.get(f"porc_{idx}", 0)
                # Manejar valores vacíos o nulos
                nota_val = float(valor) if valor and valor.strip() != '' else 0.0
                porc_val = float(porc) if porc and porc.strip() != '' else 0.0
                notas.append({
                    "nota": nota_val,
                    "porcentaje": porc_val
                })
        examen = {}
        if "examen_nota" in request.POST and request.POST.get("examen_nota"):
            examen_nota_val = request.POST.get("examen_nota")
            examen_porc_val = request.POST.get("examen_porcentaje", 0)
            examen = {
                "nota": float(examen_nota_val) if examen_nota_val and examen_nota_val.strip() != '' else 0.0,
                "porcentaje": float(examen_porc_val) if examen_porc_val and examen_porc_val.strip() != '' else 0.0
            }

        Ramo.objects.create(
            user=request.user, 
            semestre=semestre,
            nombre=nombre, 
            notas=notas, 
            examen=examen
        )
        return redirect(f"/mi_semestre/?semestre={semestre_id}")

    return render(request, "crear_ramo.html", {"semestres": semestres})

@login_required
def eliminar_ramo(request, ramo_id):
    try:
        ramo = Ramo.objects.get(id=ramo_id, user=request.user)
        semestre_id = ramo.semestre.id if ramo.semestre else None
        ramo.delete()
        if semestre_id:
            return redirect(f"/mi_semestre/?semestre={semestre_id}")
    except Ramo.DoesNotExist:
        pass
    return redirect("/mi_semestre/")

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
                # Manejar valores vacíos o nulos
                nota_val = float(valor) if valor and valor.strip() != '' else 0.0
                porc_val = float(porc) if porc and porc.strip() != '' else 0.0
                notas.append({
                    "nota": nota_val,
                    "porcentaje": porc_val
                })
        examen = {}
        if "examen_nota" in request.POST and request.POST.get("examen_nota"):
            examen_nota_val = request.POST.get("examen_nota")
            examen_porc_val = request.POST.get("examen_porcentaje", 0)
            examen = {
                "nota": float(examen_nota_val) if examen_nota_val and examen_nota_val.strip() != '' else 0.0,
                "porcentaje": float(examen_porc_val) if examen_porc_val and examen_porc_val.strip() != '' else 0.0
            }

        ramo.nombre = nombre
        ramo.notas = notas
        ramo.examen = examen
        ramo.save()
        
        semestre_id = ramo.semestre.id if ramo.semestre else None
        if semestre_id:
            return redirect(f"/mi_semestre/?semestre={semestre_id}")
        return redirect("/mi_semestre/")

    return render(request, "editar_ramo.html", {"ramo": ramo})