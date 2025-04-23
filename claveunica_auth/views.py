from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.



def claveunica_login(request):
    return HttpResponse("Redirigiendo a Clave Única...")

def claveunica_callback(request):
    return HttpResponse("Callback recibido desde Clave Única.")
