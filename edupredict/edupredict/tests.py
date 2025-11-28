from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ramo


class RamoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="eva", password="1234")

    def test_promedio_parcial(self):
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Matematicas",
            notas=[
                {"nota": 5.0, "porcentaje": 50},
                {"nota": 4.0, "porcentaje": 50}
            ],
            examen={}
        )
        self.assertEqual(ramo.promedio_parcial, 4.5)

    def test_promedio_final_con_examen(self):
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Fisica",
            notas=[
                {"nota": 5.0, "porcentaje": 60},
                {"nota": 3.0, "porcentaje": 40},
            ],
            examen={"nota": 4.0, "porcentaje": 30},
        )
        # parcial = 5*0.6 + 3*0.4 = 4.2
        # final = 4.2*0.7 + 4*0.3 = 4.14
        self.assertEqual(ramo.promedio_final, 4.14)

    def test_defcon_5(self):
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Quimica",
            notas=[{"nota": 6, "porcentaje": 100}],
            examen={}
        )
        self.assertEqual(ramo.defcon, 5)

    def test_defcon_1_reprobado(self):
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Historia",
            notas=[{"nota": 2, "porcentaje": 100}],
            examen={}
        )
        self.assertEqual(ramo.defcon, 1)

    def test_defcon_4_faltan_notas_pero_aprueba_con_1(self):
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Lenguaje",
            notas=[
                {"nota": 6, "porcentaje": 50},
                {"nota": None, "porcentaje": 50}
            ],
            examen={}
        )
        self.assertEqual(ramo.defcon, 4)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="eva",
            email="eva@test.com",
            password="1234"
        )


    def test_registro_post(self):
        response = self.client.post(reverse("registro"), {
            "username": "nuevo",
            "email": "nuevo@test.com",
            "password": "abcd"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nuevo").exists())


    def test_login_correcto(self):
        response = self.client.post(reverse("login"), {
            "email": "eva@test.com",
            "password": "1234"
        })
        self.assertEqual(response.status_code, 302) 

    def test_login_incorrecto(self):
        response = self.client.post(reverse("login"), {
            "email": "eva@test.com",
            "password": "mal"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credenciales incorrectas")

    # --- Crear ramo ---
    def test_crear_ramo(self):
        self.client.login(username="eva", password="1234")

        response = self.client.post(reverse("crear-ramo"), {
            "nombre": "Programación",
            "nota_1": "5.0",
            "porc_1": "60",
            "nota_2": "4.0",
            "porc_2": "40",
            "examen_nota": "4.5",
            "examen_porcentaje": "30"
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ramo.objects.filter(nombre="Programación").exists())


    def test_eliminar_ramo(self):
        self.client.login(username="eva", password="1234")
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Cálculo",
            notas=[],
            examen={}
        )

        response = self.client.get(reverse("eliminar-ramo", args=[ramo.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ramo.objects.filter(id=ramo.id).exists())

    # --- Editar ramo ---
    def test_editar_ramo(self):
        self.client.login(username="eva", password="1234")
        ramo = Ramo.objects.create(
            user=self.user,
            nombre="Álgebra",
            notas=[{"nota": 4, "porcentaje": 100}],
            examen={}
        )

        response = self.client.post(reverse("editar-ramo", args=[ramo.id]), {
            "nombre": "Álgebra II",
            "nota_1": "6",
            "porc_1": "100"
        })

        self.assertEqual(response.status_code, 302)

        ramo.refresh_from_db()
        self.assertEqual(ramo.nombre, "Álgebra II")
        self.assertEqual(ramo.notas[0]["nota"], 6.0)


class URLTests(TestCase):
    def test_urls_exist(self):
        urls = [
            "index",
            "registro",
            "login",
            "logout",
            "miperfil",
            "calc-sinreg",
            "calculadora",
            "mi-semestre",
            "crear-ramo"
        ]

        for u in urls:
            reverse(u)