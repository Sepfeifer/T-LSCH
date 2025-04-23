from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.claveunica_login, name='claveunica_login'),
    path('callback/', views.claveunica_callback, name='claveunica_callback'),
]
