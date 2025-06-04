from django.contrib import admin
from django.urls import path, include
from core import views
from core.views import vista_admin, login_view, vista_funcionario, traductor

urlpatterns = [
    path('', login_view, name='login'),  # Ahora el login es la página principal
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_visita, name='home_visita'),
    path('home_visita', views.home_visita, name='home_visita'),
    path('claveunica/', include('claveunica_auth.urls')),

    #Vista de usuarios
      path('vista_admin/', vista_admin, name='vista_admin'),
      path('funcionario/', vista_funcionario, name='vista_funcionario'),
      path('funcionario/traductor/', traductor, name='traductor'),

    
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

    # Traductor 
    path('funcionario/traductor/', traductor, name='traductor'),
    path('traductor/', traductor, name='traductor_directo'),
    
    # Encuesta
     # Procesar la encuesta que crea el funcionario (POST)
    path('generar_encuesta/', views.generar_encuesta, name='generar_encuesta'),
    path('encuesta/<int:encuesta_id>/', views.ver_encuesta, name='ver_encuesta'),
    path('encuesta/<int:encuesta_id>/responder/', views.responder_encuesta, name='responder_encuesta'),
    path('gestion/informes/', views.reportes, name='ver_informes'),
]