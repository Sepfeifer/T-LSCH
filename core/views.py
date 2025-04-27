from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Video
from .forms import VideoForm
from .models import Usuario


TEMPLATE_DIRS =(
    'os.path.join(BASE_DIR, "templates")'
)

def home_visita(request):
    return render(request, "home_visita.html")

def listar(request):
    users = Usuario.objects.all()
    datos = {'usuarios' : users}
    return render(request, "admin_usuario/listar.html", datos)

def agregar(request):
    if request.method == 'POST':
        if (
            request.POST.get('id_rut') and request.POST.get('nombre') and 
            request.POST.get('seg_nombre') and request.POST.get('apellido') and 
            request.POST.get('apellido_m') and request.POST.get('correo') and 
            request.POST.get('rol')
        ):
            user = Usuario()
            user.id_rut = request.POST.get('id_rut')
            user.nombre = request.POST.get('nombre')
            user.seg_nombre = request.POST.get('seg_nombre')
            user.apellido = request.POST.get('apellido')
            user.apellido_m = request.POST.get('apellido_m')
            user.correo = request.POST.get('correo')
            user.rol = request.POST.get('rol')
            user.save()
            return redirect('listar')
        else:
            return render(request, "admin_usuario/agregar.html", {
                'error': 'Todos los campos son obligatorios.'
            })
    else:
        return render(request, "admin_usuario/agregar.html")

def actualizar(request):
    if request.method == 'POST':
        if request.POST.get('id_rut') and request.POST.get('nombre') and request.POST.get('apellido') and request.POST.get('correo') and request.POST.get('rol'):
            id_user_act = request.POST.get('id')
            user_act = Usuario()
            user_act = Usuario.objects.get(id = id_user_act)

            user = Usuario()
            user.id_rut = request.POST.get('id_rut')
            user.nombre = request.POST.get('nombre')
            user.apellido =request.POST.get('apellido')
            user.correo = request.POST.get('correo')
            user.rol = request.POST.get('rol')
            user.f_registro = user_act.f_registro
            user.save()
            return redirect('listar')
    else:
        users = Usuario.objects.all()
        datos = {'usuarios' : users}
        return render(request, "admin_usuario/actualizar.html", datos)


#VIDEOS

def eliminar(request):
    if request.method== 'POST':
        if request.POST.get('id_rut'):
            u_eliminar = request.POST.get('id')
            tupla = Usuario.objects.get(id = u_eliminar)
            tupla.delete()
            return redirect('listar')
    else:
        users = Usuario.objects.all()
        datos = {'usuarios' : users}
        return render(request, "admin/eliminar.html", datos)
    
def agregar_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_videos')
    else:
        form = VideoForm()
    return render(request, 'Admin/agregar_video.html', {'form': form})


def listar_videos(request):
    videos = Video.objects.all()
    return render(request, 'Admin/listar_video.html', {'videos': videos})

def editar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            return redirect('listar_videos')
    else:
        form = VideoForm(instance=video)
    
    return render(request, 'Admin/editar_video.html', {'form': form})

def eliminar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    return redirect('listar_videos')
