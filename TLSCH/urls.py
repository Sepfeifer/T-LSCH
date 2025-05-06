"""
URL configuration for TLSCH project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('', views.home_visita, name='home_visita'),
    path('home_visita', views.home_visita, name='home_visita'),
    path('claveunica/', include('claveunica_auth.urls')),
    
    # Gestión de usuarios
    path('gestion/usuarios/', views.listar, name="listar_usuarios"),
    path('gestion/usuarios/agregar/', views.agregar, name="agregar_usuario"),
    path('gestion/usuarios/actualizar/', views.actualizar, name="actualizar_usuario"),
    path('gestion/usuarios/eliminar/', views.eliminar, name="eliminar_usuario"),
    
    # Gestión de videos
    path('gestion/videos/', views.listar_videos, name="listar_videos"),
    path('gestion/videos/agregar/', views.agregar_video, name="agregar_video"),
    path('gestion/videos/editar/<int:video_id>/', views.editar_video, name="editar_video"),
    path('gestion/videos/eliminar/<int:video_id>/', views.eliminar_video, name="eliminar_video"),
]