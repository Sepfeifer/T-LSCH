#from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_superuser(self, id_rut, email, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('es_administrador', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(id_rut, email, nombre, apellido, password, **extra_fields)

    def _create_user(self, id_rut, email, nombre, apellido, password, **extra_fields):
        if not id_rut:
            raise ValueError('The RUN must be set')
        email = self.normalize_email(email)
        user = self.model(
            id_rut=id_rut,
            email=email,
            nombre=nombre,
            apellido=apellido,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class Usuario(AbstractUser):
    username = None
    id_rut = models.CharField(
        'RUN',
        max_length=15,
        unique=True,
        primary_key=True,
        help_text='RUN sin puntos ni guión'
    )
    nombre = models.CharField('Nombre', max_length=30)
    seg_nombre = models.CharField('Segundo Nombre', max_length=30, blank=True)
    apellido = models.CharField('Apellido Paterno', max_length=30)
    apellido_m = models.CharField('Apellido Materno', max_length=30, blank=True)
    correo = models.EmailField('Correo Electrónico', unique=True)
    rol = models.CharField('Rol', max_length=20)
    f_registro = models.DateTimeField('Fecha de Registro', auto_now_add=True)
    es_administrador = models.BooleanField('Es Administrador', default=False)
    es_funcionario = models.BooleanField('Es Funcionario', default=False)

    USERNAME_FIELD = 'id_rut'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'correo', 'email']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        #db_table = 'usuario'    Esto causa problemas con mariaDB

    def __str__(self):
        return f"{self.get_full_name()} ({self.id_rut})"

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre
    
class Tema(models.Model):
        nombre = models.CharField(max_length=100, unique=True)

        def __str__(self):
            return self.nombre

class Video(models.Model):
    nombre = models.CharField(max_length=255)
    temas = models.ManyToManyField(Tema, related_name='videos')  # nuevo campo
    url_codigo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
   