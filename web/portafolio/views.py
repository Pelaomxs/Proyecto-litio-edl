import os

from django.conf import settings
from django.shortcuts import render


def _contar_slides():
    slides_dir = os.path.join(settings.BASE_DIR, "portafolio", "static", "portafolio", "slides")
    if not os.path.isdir(slides_dir):
        return 0
    return len([f for f in os.listdir(slides_dir) if f.lower().endswith(".png")])


def home(request):
    return render(request, "portafolio/home.html", {"num_slides": _contar_slides()})


def calculo_edl_evaporacion(request):
    return render(request, "portafolio/calculo_edl.html")


def calculo_sorbente(request):
    return render(request, "portafolio/calculo_sorbente.html")
