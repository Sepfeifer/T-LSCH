from django.contrib import admin
from django.urls import path, include
from core.views import login_view, logout_view
from django.views.generic import RedirectView  # Importa tus vistas de autenticación

urlpatterns = [
      # 1) Raíz → login
     path('', RedirectView.as_view(pattern_name='login', permanent=False)),
     
    # Admin site (registra el namespace 'admin')
    path('admin/', admin.site.urls),

    # Login/Logout
    path('login/',  login_view,  name='login'),
    path('logout/', logout_view, name='logout'),

    # Rutas de la app core
    path('', include('core.urls')),
]
