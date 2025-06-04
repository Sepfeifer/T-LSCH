# core/urls.py

from django.contrib import admin
from django.urls import path, include
from core import views
from core.views import vista_admin, login_view, vista_funcionario, traductor

urlpatterns = [
    # -------------------- LOGIN / LOGOUT --------------------
    path('', login_view, name='login'),                  # Página principal → login
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # -------------------- HOME VISITA --------------------
    path('', views.home_visita, name='home_visita'),
    path('home_visita', views.home_visita, name='home_visita'),
    path('claveunica/', include('claveunica_auth.urls')),

    # -------------------- VISTAS DE USUARIOS --------------------
    path('vista_admin/', vista_admin, name='vista_admin'),
    path('funcionario/', vista_funcionario, name='vista_funcionario'),

    # -------------------- TRADUCTOR (FUNCIONARIO) --------------------
    # Ahora el funcionario siempre entra sin pasar trámite_id por URL:
    path('funcionario/traductor/', views.traductor, name='traductor'),

    # Mantener la ruta “traductor directa” si la usas en algún lugar:
    path('traductor/', traductor, name='traductor_directo'),

    # -------------------- GESTIÓN DE USUARIOS --------------------
    path('gestion/usuarios/', views.listar, name="listar_usuarios"),
    path('gestion/usuarios/agregar/', views.agregar, name="agregar_usuario"),
    path('gestion/usuarios/actualizar/', views.actualizar, name="actualizar_usuario"),
    path('gestion/usuarios/eliminar/', views.eliminar, name="eliminar_usuario"),

    # -------------------- GESTIÓN DE VIDEOS --------------------
    path('gestion/videos/', views.listar_videos, name="listar_videos"),
    path('gestion/videos/agregar/', views.agregar_video, name="agregar_video"),
    path('gestion/videos/editar/<int:video_id>/', views.editar_video, name="editar_video"),
    path('gestion/videos/eliminar/<int:video_id>/', views.eliminar_video, name="eliminar_video"),

    # -------------------- CREAR ENCUESTA (FUNCIONARIO) --------------------
    path('tramite/<int:tramite_id>/crear_encuesta/', views.crear_encuesta, name='crear_encuesta'),

    # -------------------- VER ENCUESTA (USUARIO) --------------------
    path('usuario/ver_tramite/<int:tramite_id>/', views.ver_encuesta, name='ver_encuesta_usuario'),

    # -------------------- RESPONDER ENCUESTA (USUARIO) --------------------
    path('tramite/<int:tramite_id>/responder/', views.responder_encuesta, name='responder_encuesta'),

    # -------------------- RUTA PARA USUARIO SORDO-MUDO: ENVIAR CONSULTA --------------------
    path('usuario/consulta/', views.usuario_consulta, name='usuario_consulta'),
]
