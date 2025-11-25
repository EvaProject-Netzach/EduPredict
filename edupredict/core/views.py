from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    return HttpResponse("Bienvenido a EduPredict")


def welcome(request):
    return render(request, "welcome.html")


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Ya existe una cuenta con este correo.")
            return redirect("register")

        user = User.objects.create_user(username=email, email=email, password=password)
        login(request, user)
        return redirect("profile")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is None:
            if not User.objects.filter(username=email).exists():
                msg = "Cuenta no registrada."
            else:
                msg = "Contraseña incorrecta."

            return redirect(f"/error/?msg={msg}")

        login(request, user)
        return redirect("profile")

    return render(request, "login.html")


def error_view(request):
    message = request.GET.get("msg", "Ha ocurrido un error.")
    return render(request, "error.html", {"message": message})


@login_required
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})
