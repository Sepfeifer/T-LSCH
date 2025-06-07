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
    """
    Representa un tema o palabra clave en LSCH (Lengua de Señas Chilena).
    Por ejemplo: 'carnet_signo', 'rut_signo', 'acta_nacimiento_signo', etc.
    """
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Video(models.Model):
    """
    Modelo que almacena los videos asociados a uno o varios temas de LSCH.
    - 'temas' es ManyToMany con Tema, de modo que un Video puede tener
      varios tags (ej: ['carnet_signo', 'documento_signo']).
    - 'url_codigo' apunta a la URL o ruta donde está guardado ese video (mp4).
    """
    nombre = models.CharField(max_length=255)
    temas = models.ManyToManyField(Tema, related_name='videos')
    url_codigo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class Encuesta(models.Model):
     pregunta = models.CharField(max_length=255)
    # Podrías tener un campo ForeignKey al funcionario que la creó, fecha, etc.

class Opcion(models.Model):
    encuesta = models.ForeignKey(Encuesta, related_name='opciones', on_delete=models.CASCADE)
    texto = models.CharField(max_length=255)
    votos = models.PositiveIntegerField(default=0)

class Tramite(models.Model):
    frase_original = models.TextField(blank=True, default="")
    playlist = models.JSONField(default=list, blank=True)
    encuesta = models.ForeignKey(
        'Encuesta',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tramites'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trámite #{self.id}: {self.frase_original[:30]}…"


class Informe(models.Model):
    """Registro diario de videos subidos por tema."""

    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='informes')
    contador = models.PositiveIntegerField(default=0)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.tema.nombre} - {self.fecha}: {self.contador}"
