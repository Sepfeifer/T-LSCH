#from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Usuario(models.Model):
    id_rut = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=30, null=False)
    seg_nombre = models.CharField(max_length=30, null=False)
    apellido = models.CharField(max_length=30, null=False)
    apellido_m = models.CharField(max_length=30, null=False)
    correo = models.CharField(max_length=50, null=False)
    rol = models.CharField( null=False)  # Agregado max_length para 'rol'
    f_registro = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'usuario'
        
class Video(models.Model):
    nombre = models.CharField(max_length=255)
    tema = models.CharField(max_length=255)
    url_codigo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre