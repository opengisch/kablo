# Create your views here.
from django.http import FileResponse
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def demo_qgis_project(request):
    return FileResponse(open("/kablo/qgis/kablo.qgs", "rb"))
