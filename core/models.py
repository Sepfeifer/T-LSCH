from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Usuario(models.Model):
    id_rut = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=30, null=False)
    seg_nombre = models.CharField(max_length=30, null=False)
    apellido = models.CharField(max_length=30, null=False)
    apellido_m = models.CharField(max_length=30, null=False)
    correo = models.CharField(max_length=50, null=False)
    rol = models.CharField(null=False)
    f_registro =models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'usuario'
