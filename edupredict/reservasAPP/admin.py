from django.contrib import admin

from reservasAPP.models import *

# Register your models here.

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'fecha', 'hora', 'cantidad', 'estado', 'observacion')
admin.site.register(Reserva, ReservaAdmin)


class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado')
admin.site.register(Estado, EstadoAdmin)