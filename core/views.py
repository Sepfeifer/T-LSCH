from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail  # ← AÑADIDO
from django.conf import settings         # ← AÑADIDO
from .models import Usuario, Video
from .forms import VideoForm

def home_visita(request):
    return render(request, "home_visita.html")

# USUARIOS
def listar(request):
    users = Usuario.objects.all()
    return render(request, "admin_usuario/listar.html", {'usuarios': users})

def agregar(request):
    print("\n--- DEBUG: INICIO VISTA AGREGAR ---")  # Debug 1
    print("Método HTTP:", request.method)  # Debug 2
    
    if request.method == 'POST':
        print("\nDEBUG: Datos recibidos del formulario:")  # Debug 3
        print("POST data:", request.POST)  # Muestra todos los datos enviados
        
        campos = ['id_rut', 'nombre', 'seg_nombre', 'apellido', 'apellido_m', 'correo', 'rol', 'clave']
        if all(request.POST.get(campo) for campo in campos):
            print("\nDEBUG: Todos los campos están presentes")  # Debug 4
            
            id_rut = request.POST['id_rut']
            correo = request.POST['correo']
            clave = request.POST['clave']

            # Verifica si el usuario ya existe
            if Usuario.objects.filter(id_rut=id_rut).exists():
                print("DEBUG: RUT ya existe en la base de datos")  # Debug 5
                return render(request, "admin_usuario/agregar.html", {'error': 'El RUT ya está registrado.'})

            try:
                print("\nDEBUG: Intentando crear Usuario...")  # Debug 6
                # Crea el usuario en tu modelo Usuario
                usuario = Usuario.objects.create(
                    id_rut=id_rut,
                    nombre=request.POST['nombre'],
                    seg_nombre=request.POST['seg_nombre'],
                    apellido=request.POST['apellido'],
                    apellido_m=request.POST['apellido_m'],
                    correo=correo,
                    rol=request.POST['rol']
                )
                print("DEBUG: Usuario creado exitosamente:", usuario)  # Debug 7

                print("\nDEBUG: Intentando crear User de Django...")  # Debug 8
                # Crea el usuario en el modelo User de Django (para autenticación)
                user = User.objects.create_user(
                    username=id_rut,
                    email=correo,
                    password=clave,
                    first_name=request.POST['nombre'],
                    last_name=request.POST['apellido']
                )
                print("DEBUG: User de Django creado exitosamente:", user)  # Debug 9

                return redirect('listar_usuarios')  # Redirige a la lista de usuarios

            except Exception as e:
                print("\nDEBUG: Error al crear usuario:", str(e))  # Debug 10
                return render(request, "admin_usuario/agregar.html", {'error': f'Ocurrió un error: {str(e)}'})

        else:
            print("\nDEBUG: Faltan campos obligatorios")  # Debug 11
            print("Campos recibidos:", {campo: request.POST.get(campo) for campo in campos})  # Debug 12
            return render(request, "admin_usuario/agregar.html", {'error': 'Todos los campos son obligatorios.'})
    
    return render(request, "admin_usuario/agregar.html")

def actualizar(request):
    usuario = None
    rut_seleccionado = request.GET.get('rut') or request.POST.get('id_rut')
    
    if rut_seleccionado:
        try:
            usuario = Usuario.objects.get(id_rut=rut_seleccionado)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    if request.method == 'POST' and usuario:
        # Actualización de campos
        usuario.nombre = request.POST.get('nombre')
        usuario.seg_nombre = request.POST.get('seg_nombre')
        usuario.apellido = request.POST.get('apellido')
        usuario.apellido_m = request.POST.get('apellido_m')
        usuario.correo = request.POST.get('correo')
        usuario.rol = request.POST.get('rol')
        
        # Actualizar contraseña solo si se proporcionó
        nueva_clave = request.POST.get('clave')
        if nueva_clave:
            user_django = User.objects.get(username=usuario.id_rut)
            user_django.set_password(nueva_clave)
            user_django.save()
        
        usuario.save()
        messages.success(request, "¡Usuario actualizado correctamente!")
        return redirect('listar_usuarios')

    return render(request, "admin_usuario/actualizar.html", {
        'usuarios': Usuario.objects.all(),
        'usuario': usuario
    })

def eliminar(request):
    usuario = None
    rut_seleccionado = request.GET.get('rut') or request.POST.get('id_rut')
    
    if rut_seleccionado:
        try:
            usuario = Usuario.objects.get(id_rut=rut_seleccionado)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    if request.method == 'POST' and usuario:
        try:
            # Eliminar también el usuario de autenticación de Django
            User.objects.filter(username=usuario.id_rut).delete()
            usuario.delete()
            messages.success(request, f"Usuario {usuario.nombre} eliminado correctamente")
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f"Error al eliminar: {str(e)}")

    return render(request, "admin_usuario/eliminar.html", {
        'usuarios': Usuario.objects.all(),
        'usuario': usuario
    })

# VIDEOS
def agregar_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_videos')
    else:
        form = VideoForm()
    return render(request, 'admin_usuario/agregar_video.html', {'form': form})

def listar_videos(request):
    videos = Video.objects.all()
    return render(request, 'admin_usuario/listar_video.html', {'videos': videos})

def editar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    form = VideoForm(request.POST or None, instance=video)
    if form.is_valid():
        form.save()
        return redirect('listar_videos')
    return render(request, 'admin_usuario/editar_video.html', {'form': form})

def eliminar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    return redirect('listar_videos')
