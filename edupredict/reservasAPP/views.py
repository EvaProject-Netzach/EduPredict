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
from django.db.models import Count
from django.contrib import messages


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
        
        if cantidad > 0 and cantidad <= 10:  # CAMBIÉ DE 8 A 10
            # Eliminar semestres existentes del usuario
            Semestre.objects.filter(user=request.user).delete()
            
            # Crear nuevos semestres
            for i in range(1, cantidad + 1):
                Semestre.objects.create(
                    user=request.user,
                    nombre=f"{i}° Semestre",
                    orden=i
                )
            
            # Agregar mensaje de éxito
            messages.success(request, f'Se crearon {cantidad} semestres exitosamente.')
            
            # Redirigir al primer semestre
            primer_semestre = Semestre.objects.filter(user=request.user).first()
            if primer_semestre:
                return redirect(f"/mi_semestre/?semestre={primer_semestre.id}")
        else:
            messages.error(request, 'Debes seleccionar una cantidad válida de semestres (1-10).')
    
    return redirect("miSemestre")

@login_required
def estadisticas(request):
    # Obtener semestres que tienen al menos 1 ramo
    semestres_con_ramos = Semestre.objects.filter(
        user=request.user,
        ramo__isnull=False
    ).distinct().order_by('orden')
    
    # Verificar si hay al menos 2 semestres con ramos
    if semestres_con_ramos.count() < 2:
        return render(request, "estadisticas.html", {
            "error": "Necesitas tener ramos en al menos 2 semestres diferentes para ver las estadísticas.",
            "semestres_con_ramos": semestres_con_ramos
        })
    
    semestre1_id = request.GET.get('semestre1')
    semestre2_id = request.GET.get('semestre2')
    
    semestre1 = None
    semestre2 = None
    ramos_semestre1 = []
    ramos_semestre2 = []
    
    if semestre1_id and semestre2_id and semestre1_id != semestre2_id:
        semestre1 = get_object_or_404(Semestre, id=semestre1_id, user=request.user)
        semestre2 = get_object_or_404(Semestre, id=semestre2_id, user=request.user)
        
        # CRÍTICO: Mantener el orden de creación (por ID) para que coincida con las tablas
        ramos_semestre1 = list(Ramo.objects.filter(user=request.user, semestre=semestre1).order_by('id'))
        ramos_semestre2 = list(Ramo.objects.filter(user=request.user, semestre=semestre2).order_by('id'))
    
    # Calcular promedios generales
    promedio_general1 = 0
    promedio_general2 = 0
    
    if ramos_semestre1:
        suma1 = sum(ramo.promedio_final for ramo in ramos_semestre1)
        promedio_general1 = round(suma1 / len(ramos_semestre1), 2)
    
    if ramos_semestre2:
        suma2 = sum(ramo.promedio_final for ramo in ramos_semestre2)
        promedio_general2 = round(suma2 / len(ramos_semestre2), 2)
    
    # DEBUG: Imprimir para verificar
    print("=== DEBUG VIEWS.PY ===")
    print(f"Semestre 1: {semestre1.nombre if semestre1 else 'None'}")
    print(f"Ramos S1: {[r.nombre for r in ramos_semestre1]}")
    print(f"Promedios S1: {[r.promedio_final for r in ramos_semestre1]}")
    print(f"Semestre 2: {semestre2.nombre if semestre2 else 'None'}")
    print(f"Ramos S2: {[r.nombre for r in ramos_semestre2]}")
    print(f"Promedios S2: {[r.promedio_final for r in ramos_semestre2]}")
    
    return render(request, "estadisticas.html", {
        "semestres_con_ramos": semestres_con_ramos,
        "semestre1": semestre1,
        "semestre2": semestre2,
        "ramos_semestre1": ramos_semestre1,
        "ramos_semestre2": ramos_semestre2,
        "promedio_general1": promedio_general1,
        "promedio_general2": promedio_general2
    })

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
        if form.isvalid():
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
            messages.warning(request, "Debes seleccionar un semestre.")
            return render(request, "crear_ramo.html", {"semestres": semestres})
            
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
        
        # Mensaje de éxito y permanecer en la página
        messages.success(request, f'El ramo "{nombre}" fue creado exitosamente en {semestre.nombre}.')
        return render(request, "crear_ramo.html", {"semestres": semestres})

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


@login_required
def filtrar_ramos(request):
    rango = request.GET.get('rango')
    ramos_filtrados = {}
    
    if rango:
        # Definir los rangos
        if rango == 'reprobados':
            min_nota, max_nota = 0.0, 3.9
            nombre_rango = 'Reprobados (0.0 - 3.9)'
        elif rango == 'aprobados_bajos':
            min_nota, max_nota = 4.0, 4.9
            nombre_rango = 'Aprobados Bajos (4.0 - 4.9)'
        elif rango == 'aprobados_medios':
            min_nota, max_nota = 5.0, 6.9
            nombre_rango = 'Aprobados Medios (5.0 - 6.9)'
        elif rango == 'excelencia':
            min_nota, max_nota = 7.0, 7.0
            nombre_rango = 'Excelencia (7.0)'
        else:
            min_nota, max_nota = None, None
            nombre_rango = ''
        
        if min_nota is not None:
            # Obtener todos los semestres del usuario
            semestres = Semestre.objects.filter(user=request.user).order_by('orden')
            
            for semestre in semestres:
                # Filtrar ramos por promedio final
                if rango == 'excelencia':
                    ramos = Ramo.objects.filter(
                        user=request.user,
                        semestre=semestre
                    ).order_by('nombre')
                    # Filtrar manualmente para excelencia (exactamente 7.0)
                    ramos = [r for r in ramos if r.promedio_final == 7.0]
                else:
                    ramos = Ramo.objects.filter(
                        user=request.user,
                        semestre=semestre
                    ).order_by('nombre')
                    # Filtrar manualmente por rango
                    ramos = [r for r in ramos if min_nota <= r.promedio_final <= max_nota]
                
                if ramos:
                    ramos_filtrados[semestre] = ramos
        
        return render(request, "filtrar_ramos.html", {
            "ramos_filtrados": ramos_filtrados,
            "nombre_rango": nombre_rango,
            "rango_seleccionado": rango
        })
    
    return render(request, "filtrar_ramos.html")

def enviar_comentario(request):
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Comentario enviado exitosamente! Gracias por contactarnos.')
            return redirect('landing')
        else:
            # Si hay errores, volver al landing con los errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
            return redirect('landing')
    return redirect('landing')