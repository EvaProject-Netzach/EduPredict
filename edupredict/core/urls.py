from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("profile/", views.profile_view, name="profile"),
    path("error/", views.error_view, name="error"),

]