# core/urls.py

from django.urls import path, include
from django.contrib.auth.decorators import login_required
from core import views

urlpatterns = [
    # ─── LOGIN / LOGOUT ───────────────────────────────────────
    path('',       views.login_view,  name='login'),
    path('login/', views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ─── HOME PÚBLICO ─────────────────────────────────────────
    path('home_visita/', views.home_visita, name='home_visita'),
    path('claveunica/', include('claveunica_auth.urls')),

    # ─── USUARIO SORDO-MUDO (público) ────────────────────────
    path('usuario/consulta/', views.usuario_consulta, name='usuario_consulta'),
    path('usuario/ver_tramite/<int:tramite_id>/', views.ver_encuesta, name='ver_encuesta_usuario'),
    path('tramite/<int:tramite_id>/responder/', views.responder_encuesta, name='responder_encuesta'),

    # ─── ADMINISTRADOR (requiere login y rol “admin”) ──────────
    path('vista_admin/', login_required(views.vista_admin), name='vista_admin'),
    path('gestion/usuarios/', login_required(views.listar), name='listar_usuarios'),
    path('gestion/usuarios/agregar/', login_required(views.agregar), name='agregar_usuario'),
    path('gestion/usuarios/actualizar/', login_required(views.actualizar), name='actualizar_usuario'),
    path('gestion/usuarios/eliminar/', login_required(views.eliminar), name='eliminar_usuario'),
    path('gestion/videos/', login_required(views.listar_videos), name='listar_videos'),
    path('gestion/videos/agregar/', login_required(views.agregar_video), name='agregar_video'),
    path('gestion/videos/editar/<int:video_id>/', login_required(views.editar_video), name='editar_video'),
    path('gestion/videos/eliminar/<int:video_id>/', login_required(views.eliminar_video), name='eliminar_video'),

    # ─── FUNCIONARIO (requiere login y rol “funcionario”) ──────
    path('funcionario/', login_required(views.vista_funcionario), name='vista_funcionario'),
    path('funcionario/traductor/', login_required(views.traductor), name='traductor'),
    path('tramite/<int:tramite_id>/crear_encuesta/', login_required(views.crear_encuesta), name='crear_encuesta'),
]
