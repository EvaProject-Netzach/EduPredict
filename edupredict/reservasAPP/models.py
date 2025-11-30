from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Estado(models.Model):
    estado = models.CharField(max_length=20)

    def __str__(self):
        return self.estado
    

class Reserva(models.Model):
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    fecha = models.DateField()
    hora = models.TimeField()
    cantidad = models.IntegerField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    observacion = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Semestre(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    orden = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['orden']
        unique_together = ['user', 'orden']
    
    def __str__(self):
        return self.nombre

# DEFINE la mayoria LO DE LOS RAMOS, OSEA promedios, calculos de formulas y weas
class Ramo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    notas = models.JSONField(default=list)  # Lista de dicts {"nota":float, "porcentaje":float}
    examen = models.JSONField(default=dict) # {"nota": float, "porcentaje": float} o {}

    @property
    def promedio_parcial(self):
        total = 0
        suma_porcentajes = 0
        for n in self.notas:
            if n.get("nota") is not None and n["nota"] != 0.0:
                total += n["nota"] * n["porcentaje"]/100
                suma_porcentajes += n["porcentaje"]
        if suma_porcentajes == 0:
            return 0
        return round(total / (suma_porcentajes/100), 2)

    @property
    def promedio_final(self):
        parcial = self.promedio_parcial
        examen_nota = self.examen.get("nota")
        examen_porc = self.examen.get("porcentaje", 0)

        if examen_nota is not None and examen_nota != 0.0:
            final = parcial * (100 - examen_porc)/100 + examen_nota * examen_porc/100
        else:
            final = parcial
        return round(final, 2)

    @property # DEFINIR SISTEMA DE ALERTAS DEFCON
    def defcon(self):
        notas = self.notas
        examen_nota = self.examen.get("nota")
        examen_porc = self.examen.get("porcentaje", 0)
        
        # Contar notas pendientes (None o 0.0)
        faltantes = sum(1 for n in notas if n["nota"] is None or n["nota"] == 0.0)

        def promedio_final_simulado(nota_pendiente=1.0):
            """Calcula el promedio final simulado con una nota para lo pendiente"""
            total = 0
            suma_porcentajes = 0
            for n in notas:
                val = n["nota"] if n["nota"] is not None and n["nota"] != 0.0 else nota_pendiente
                total += val * n["porcentaje"]/100
                suma_porcentajes += n["porcentaje"]
            
            # Calcular promedio parcial simulado
            if suma_porcentajes > 0:
                parcial_simulado = total / (suma_porcentajes/100)
            else:
                parcial_simulado = 0
            
            # Calcular promedio final considerando examen
            if examen_nota is not None and examen_nota != 0.0:
                final = parcial_simulado * (100 - examen_porc)/100 + examen_nota * examen_porc/100
            else:
                final = parcial_simulado
            
            return round(final, 2)

        # DEFCON 5: completado y promedio final mayor o igual a 3.95
        if faltantes == 0 and (examen_nota is not None or examen_porc == 0) and self.promedio_final >= 3.95:
            return 5

        # DEFCON 1: completado y reprobado
        if faltantes == 0 and self.promedio_final < 3.95:
            return 1

        # si faltan notas
        if faltantes >= 1:
            peor_caso = promedio_final_simulado(1.0)

            # DEFCON 4: parcialmente completado, con 1.0 aun apruebas con mas de 3.95
            if peor_caso >= 3.95:
                return 4

            # Si faltan 2 o más notas, DEFCON 3
            if faltantes >= 2:
                return 3

            # Si falta solo 1 nota
            if faltantes == 1:
                # Calcular la nota mínima necesaria en la nota pendiente para aprobar
                puntos_actuales = 0
                porcentaje_total = 0
                porcentaje_pendiente = 0
                
                # Sumar puntos de notas existentes
                for n in notas:
                    if n["nota"] is not None and n["nota"] != 0.0:
                        puntos_actuales += n["nota"] * n["porcentaje"]/100
                    porcentaje_total += n["porcentaje"]
                    if n["nota"] is None or n["nota"] == 0.0:
                        porcentaje_pendiente = n["porcentaje"]
                
                # Considerar el examen en el cálculo
                if examen_nota is not None and examen_nota != 0.0:
                    # Con examen: puntos_actuales representa el parcial, necesitamos calcular la nota necesaria
                    # para que el final sea >= 3.95
                    # Fórmula: final = (parcial * (100 - examen_porc) + examen_nota * examen_porc) / 100
                    # Necesitamos: (parcial * (100 - examen_porc) + examen_nota * examen_porc) / 100 >= 3.95
                    # parcial >= (3.95 * 100 - examen_nota * examen_porc) / (100 - examen_porc)
                    parcial_necesario = (3.95 * 100 - examen_nota * examen_porc) / (100 - examen_porc)
                    # Ahora calculamos la nota necesaria en la nota pendiente para alcanzar ese parcial
                    puntos_necesarios_parcial = parcial_necesario * (porcentaje_total/100) - puntos_actuales
                else:
                    # Sin examen: necesitamos promedio parcial >= 3.95
                    puntos_necesarios_parcial = 3.95 * (porcentaje_total/100) - puntos_actuales
                
                if porcentaje_pendiente > 0:
                    nota_necesaria = (puntos_necesarios_parcial * 100) / porcentaje_pendiente
                else:
                    nota_necesaria = 7.0
                
                # Ajustar por posibles errores de redondeo
                nota_necesaria = max(0, nota_necesaria)
                
                if nota_necesaria <= 4.94:
                    return 3
                elif nota_necesaria <= 7.0:
                    return 2
                else:
                    return 1

        # Por default
        return 1

    def __str__(self):
        return self.nombre