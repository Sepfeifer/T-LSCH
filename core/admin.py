from django.contrib import admin
from .models import Usuario
from django.contrib.auth.admin import UserAdmin
# Register your models here.



class CustomUserAdmin(UserAdmin):
    # Especifica el campo de ordenación (usa 'id_rut' en lugar de 'username')
    ordering = ('id_rut',)
    
    # Personaliza los campos mostrados en el admin
    list_display = ('id_rut', 'email', 'nombre', 'apellido', 'is_staff')
    search_fields = ('id_rut', 'email', 'nombre', 'apellido')
    
    # Ajusta los fieldset para incluir tus campos personalizados
    fieldsets = (
        (None, {'fields': ('id_rut', 'password')}),
        ('Información personal', {'fields': ('nombre', 'seg_nombre', 'apellido', 'apellido_m', 'email', 'correo')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Usuario, CustomUserAdmin)