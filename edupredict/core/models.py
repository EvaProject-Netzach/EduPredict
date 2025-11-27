from django.db import models
from django.contrib.auth.models import User

# DEFINE la mayoria LO DE LOS RAMOS, OSEA promedios, calculos de formulas y weas
class Ramo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    notas = models.JSONField(default=list)  # Lista de dicts {"nota":float, "porcentaje":float}
    examen = models.JSONField(default=dict) # {"nota": float, "porcentaje": float} o {}

    @property
    def promedio_parcial(self):
        total = 0
        suma_porcentajes = 0
        for n in self.notas:
            if n.get("nota") is not None:
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

        if examen_nota is not None:
            final = parcial * (100 - examen_porc)/100 + examen_nota * examen_porc/100
        else:
            final = parcial
        return round(final, 2)

    @property # DEFINIR SISTEMA DE ALERTAS DEFCON
    def defcon(self):
        notas = self.notas
        examen_nota = self.examen.get("nota")
        examen_porc = self.examen.get("porcentaje", 0)
        faltantes = sum(1 for n in notas if n["nota"] is None)

        def promedio_simulado(nota_pendiente=1.0):
            total = 0
            suma_porcentajes = 0
            for n in notas:
                val = n["nota"] if n["nota"] is not None else nota_pendiente
                total += val * n["porcentaje"]/100
                suma_porcentajes += n["porcentaje"]
            parcial = total / (suma_porcentajes/100) if suma_porcentajes else 0
            if examen_nota is not None:
                final = parcial * (100 - examen_porc)/100 + examen_nota * examen_porc/100
            else:
                final = parcial
            return round(final, 2)

        # DEFCON 5: completado y promedio final mayor o igual a 3.95
        if faltantes == 0 and (examen_nota is not None or examen_porc == 0) and self.promedio_final >= 3.95:
            return 5

        # DEFCON 1: completado y reprobado
        if faltantes == 0 and self.promedio_final < 3.95:
            return 1

        # si faltan notas
        if faltantes >= 1:
            peor_caso = promedio_simulado(1.0)

            # DEFCON 4: parcialmente completado, con 1.0 aun apruebas con mas de 3.95
            if peor_caso >= 3.95:
                return 4

            # DEFCON 3: faltan 2 notas o la última nota pendiente requiere entre 1.1 y 4.94
            if faltantes >= 2:
                return 3

            if faltantes == 1:
                # Calculamos nota minima necesaria para aprobar osea SOBRE 3.95 NO 4.0
                nota_necesaria = 3.95 * 100 / notas[-1]["porcentaje"]  # aproximación simple
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
