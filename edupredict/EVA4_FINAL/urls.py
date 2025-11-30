"""
URL configuration for EVA4_FINAL project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from reservasAPP.views import crear_ramo
from reservasAPP.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("usuarios/", include("reservasAPP.urls")),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
    path("index/", TemplateView.as_view(template_name="index.html"), name="home"),
    path("calculadora_sin_registro/", TemplateView.as_view(template_name="calculadora_sin_registro.html"), name="calculoRapido"),
    path("crear_ramo/", crear_ramo, name="crearRamo"),
    path("mi_semestre/", mi_semestre, name="miSemestre"),
    path("crear-semestres/", crear_semestres, name="crear-semestres"),
    path("editar-ramo/<int:ramo_id>/", editar_ramo, name="editar-ramo"),
    path("eliminar-ramo/<int:ramo_id>/", eliminar_ramo, name="eliminar-ramo"),


    path('reservas/', reservasData, name='reservas'),
    path('registroReservas', registroReservas, name="registroReservas"),
    path('eliminarReservas/<int:id>', eliminarReservas, name="eliminarReservas"),
    path('editarReservas/<int:id>', editarReservas, name="editarReservas"),

    path('estados/', estadosData, name='estados'),
    path('registroEstados', registroEstados, name="registroEstados"),
    path('eliminarEstados/<int:id>', eliminarEstados, name="eliminarEstados"),
    path('editarEstados/<int:id>', editarEstados, name="editarEstados"),

    path('reservasAPI/', lista_reservas),
    path("accounts/", include("django.contrib.auth.urls")), # Todas las urls de autenticación
    path('reservasAPI/<int:pk>/', detalle_reservas),
]