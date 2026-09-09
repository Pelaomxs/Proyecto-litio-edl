from django.urls import path

from . import views

app_name = "portafolio"

urlpatterns = [
    path("", views.home, name="home"),
    path("calculo/edl-vs-evaporacion/", views.calculo_edl_evaporacion, name="calculo_edl"),
    path("calculo/sorbente/", views.calculo_sorbente, name="calculo_sorbente"),
]
