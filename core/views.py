import re
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail  # ← AÑADIDO
from django.conf import settings         # ← AÑADIDO
from .models import Usuario, Video, Tema, Encuesta, Opcion, Informe
from .forms import VideoForm
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .services.spacy_translator import  translate_to_lsch
from .services.spacy_extractor import extract_keywords_spacy
from .services.synonym_service import get_synonyms
from datetime import timedelta
from django.db.models import Sum

logger = logging.getLogger(__name__)

#Login  
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.es_administrador:
            return redirect('vista_admin')
        elif request.user.es_funcionario:
            return redirect('vista_funcionario')
        return redirect('home_visita')
    
    if request.method == 'POST':
        run = request.POST.get('run')
        password = request.POST.get('password')
        user = authenticate(request, username=run, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser or user.es_administrador:
                return redirect('vista_admin')
            elif user.es_funcionario:
                return redirect('vista_funcionario')
            return redirect('home_visita')
        else:
            return render(request, 'login/login.html', {
                'error': 'RUN o contraseña incorrectos',
                'run': run
            })
    
    return render(request, 'login/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def vista_funcionario(request):
    if not request.user.es_funcionario and not request.user.is_superuser:
        return redirect('login')
    return render(request, 'vista_funcionario.html')

def home_visita(request):
    return render(request, "home_visita.html")

#ADMIN_VISTA    
def vista_admin(request):
    
    return render(request, 'vista_admin.html')

# USUARIOS
def listar(request):
    users = Usuario.objects.all()
    return render(request, "admin_usuario/listar.html", {'usuarios': users})

def agregar(request):
    logger.debug("\n--- DEBUG: INICIO VISTA AGREGAR ---")
    logger.debug("Método HTTP: %s", request.method)
    
    if request.method == 'POST':
        logger.debug("\nDEBUG: Datos recibidos del formulario:")
        logger.debug("POST data: %s", request.POST)
        
        campos = ['id_rut', 'nombre', 'seg_nombre', 'apellido', 'apellido_m', 'correo', 'rol', 'clave']
        if all(request.POST.get(campo) for campo in campos):
            logger.debug("\nDEBUG: Todos los campos están presentes")
            
            id_rut = request.POST['id_rut']
            correo = request.POST['correo']
            clave = request.POST['clave']

            # Verifica si el usuario ya existe
            if Usuario.objects.filter(id_rut=id_rut).exists():
                logger.debug("DEBUG: RUT ya existe en la base de datos")
                return render(request, "admin_usuario/agregar.html", {'error': 'El RUT ya está registrado.'})

            try:
                logger.debug("\nDEBUG: Intentando crear Usuario...")
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
                logger.debug("DEBUG: Usuario creado exitosamente: %s", usuario)

                logger.debug("\nDEBUG: Intentando crear User de Django...")
                # Crea el usuario en el modelo User de Django (para autenticación)
                user = User.objects.create_user(
                    username=id_rut,
                    email=correo,
                    password=clave,
                    first_name=request.POST['nombre'],
                    last_name=request.POST['apellido']
                )
                logger.debug("DEBUG: User de Django creado exitosamente: %s", user)

                return redirect('listar_usuarios')  # Redirige a la lista de usuarios

            except Exception as e:
                logger.error("\nDEBUG: Error al crear usuario: %s", str(e))
                return render(request, "admin_usuario/agregar.html", {'error': f'Ocurrió un error: {str(e)}'})

        else:
            logger.debug("\nDEBUG: Faltan campos obligatorios")
            logger.debug("Campos recibidos: %s", {campo: request.POST.get(campo) for campo in campos})
            return render(request, "admin_usuario/agregar.html", {'error': 'Todos los campos son obligatorios.'})
    
    return render(request, "admin_usuario/agregar.html") 

def actualizar(request):
    # Obtener el modelo de usuario personalizado
    Usuario = get_user_model()
    
    usuario = None
    rut_seleccionado = request.GET.get('rut') or request.POST.get('id_rut')
    
    if rut_seleccionado:
        try:
            # Usar directamente el modelo personalizado
            usuario = Usuario.objects.get(id_rut=rut_seleccionado)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect('actualizar_usuario')

    if request.method == 'POST' and usuario:
        try:
            # Actualización de campos básicos
            usuario.nombre = request.POST.get('nombre')
            usuario.seg_nombre = request.POST.get('seg_nombre', '')
            usuario.apellido = request.POST.get('apellido')
            usuario.apellido_m = request.POST.get('apellido_m', '')
            usuario.correo = request.POST.get('correo')
            usuario.rol = request.POST.get('rol')
            
            # Actualizar contraseña si se proporcionó
            nueva_clave = request.POST.get('clave')
            if nueva_clave:
                usuario.set_password(nueva_clave)
            
            usuario.save()
            messages.success(request, "¡Usuario actualizado correctamente!")
            return redirect('listar_usuarios')
            
        except Exception as e:
            messages.error(request, f"Error al actualizar usuario: {str(e)}")

    return render(request, "admin_usuario/actualizar.html", {
        'usuarios': Usuario.objects.all(),
        'usuario': usuario
    })

def eliminar(request):
    Usuario = get_user_model()  # Obtenemos el modelo personalizado
    
    usuario = None
    rut_seleccionado = request.GET.get('rut') or request.POST.get('id_rut')
    
    if rut_seleccionado:
        try:
            usuario = Usuario.objects.get(id_rut=rut_seleccionado)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect('eliminar_usuario')

    if request.method == 'POST' and usuario:
        try:
            # Eliminar el usuario (ya no necesitamos eliminar de User)
            nombre_usuario = usuario.get_full_name()
            usuario.delete()
            messages.success(request, f"Usuario {nombre_usuario} eliminado correctamente")
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f"Error al eliminar: {str(e)}")
            return redirect('eliminar_usuario')

    return render(request, "admin_usuario/eliminar.html", {
        'usuarios': Usuario.objects.all(),
        'usuario': usuario
    })

# VIDEOS
def agregar_video(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        temas_ingresados = post_data.getlist('temas')

        # Crea o obtiene los temas escritos por el usuario
        tema_objs = []
        for t in temas_ingresados:
            tema_obj, _ = Tema.objects.get_or_create(nombre=t.strip())
            tema_objs.append(tema_obj)

        # Crear el formulario sin asignar aún los temas
        form = VideoForm(post_data)
        if form.is_valid():
            video = form.save(commit=False)
            video.save()
            video.temas.set(tema_objs)  # Asignar temas ManyToMany
            return redirect('listar_videos')
    else:
        form = VideoForm()
    return render(request, 'admin_usuario/agregar_video.html', {'form': form})


def listar_videos(request):
    videos = Video.objects.all()
    return render(request, 'admin_usuario/listar_video.html', {'videos': videos})

def editar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            video = form.save(commit=False)
            video.save()
            form.save_m2m()
            return redirect('listar_videos')
    else:
        form = VideoForm(instance=video)

    return render(request, 'admin_usuario/editar_video.html', {'form': form, 'video': video})

def eliminar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    return redirect('listar_videos')




def traductor(request):
    """
    Vista que recibe un texto (POST), lo tokeniza respetando comillas,
    busca cada token en Video.nombre o sus sinónimos y arma la lista 'playlist'.
    Al final guarda 'playlist' en sesión para que luego la encuesta la pueda reproducir.
    """
    frase = ""
    playlist = []
    matches = {}

    if request.method == "POST":
        frase = request.POST.get("frase", "").strip()
        if frase:
            # 1) Separar tokens, pero si hay algo entre comillas, desmenúzalo por letra
            tokens = []
            for m in re.finditer(r'"([^"]+)"|(\S+)', frase):
                if m.group(1) is not None:
                    # Dentro de comillas: cada carácter (omitir espacios)
                    for ch in m.group(1):
                        if ch.strip():
                            tokens.append(ch.lower())
                else:
                    # Token normal
                    tokens.append(m.group(2).lower())

            # 2) Por cada token, buscar video por nombre o sinónimo
            for token in tokens:
                video = Video.objects.filter(nombre__iexact=token).first()
                if not video:
                    video = Video.objects.filter(nombre__icontains=token).first()

                if not video:
                    for syn in get_synonyms(token):
                        video = Video.objects.filter(nombre__icontains=syn).first()
                        if video:
                            break

                if video:
                    # Incrementar el contador de informes por cada tema asociado
                    today = timezone.now().date()
                    for tema in video.temas.all():
                        informe, _ = Informe.objects.get_or_create(
                            tema=tema, fecha=today
                        )
                        informe.cantidad += 1
                        informe.save()

                    url = video.url_codigo.strip()
                    if "youtube.com" in url or "youtu.be" in url:
                        # Extraer ID de YouTube
                        video_id = None
                        if "watch?v=" in url:
                            after = url.split("watch?v=")[1]
                            video_id = after.split("&")[0]
                        elif "youtu.be/" in url:
                            after = url.split("youtu.be/")[1]
                            video_id = after.split("?")[0]
                        if video_id:
                            embed = f"https://www.youtube.com/embed/{video_id}?enablejsapi=1&autoplay=1"
                        else:
                            embed = url
                        playlist.append({
                            "titulo": video.nombre,
                            "url": embed,
                            "is_youtube": True,
                        })
                    else:
                        playlist.append({
                            "titulo": video.nombre,
                            "url": video.url_codigo,
                            "is_youtube": False,
                        })

                    # Guardar coincidencia para mostrar texto de matches
                    matches[token] = video.nombre

            # 3) Guardar la playlist en sesión para que la encuesta pública la reproduzca
            request.session['ultima_playlist'] = playlist

    return render(request, "traductor.html", {
        "frase": frase,
        "playlist": playlist,
        "matches": matches,
    })


def generar_encuesta(request):
    """
    Recibe el POST desde el segundo formulario de traductor.html (action="/generar_encuesta/").
    Crea una Encuesta y sus Opciones, luego redirige a /encuesta/<id>/.
    """
    if request.method == "POST":
        pregunta = request.POST.get('encuestaPregunta', '').strip()
        opciones = [v.strip() for v in request.POST.getlist('opcion') if v.strip()]
        if pregunta and len(opciones) >= 2:
            # 1) Crear modelo Encuesta
            encuesta = Encuesta.objects.create(pregunta=pregunta)
            # 2) Crear cada Opcion
            for texto in opciones:
                Opcion.objects.create(encuesta=encuesta, texto=texto)
            # 3) Redirigir a la página pública de la encuesta
            return redirect('ver_encuesta', encuesta_id=encuesta.id)
    # Si algo está mal (pregunta vacía o <2 opciones), volver a la vista del traductor
    return redirect('traductor')


def ver_encuesta(request, encuesta_id):
    """
    Muestra la encuesta para que el usuario (sordo-mudo) vote. También reproduce
    la ‘ultima_playlist’ que guardó el funcionario en sesión desde /traductor/.
    """
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    playlist = request.session.get('ultima_playlist', [])

    return render(request, 'usuario/ver_encuesta.html', {
        'encuesta': encuesta,
        'playlist': playlist,
    })


def responder_encuesta(request, encuesta_id):
    """
    Procesa el POST cuando el usuario final envía su voto.
    """
    if request.method == "POST":
        opcion_id = request.POST.get('opcion_sel')
        if opcion_id:
            opcion = get_object_or_404(Opcion, id=int(opcion_id), encuesta_id=encuesta_id)
            opcion.votos += 1
            opcion.save()
            # Aquí rediriges a una página de “Gracias por votar” si quieres,
            # o a la misma vista de resultados. Por ahora:
            return redirect('agradecimiento_encuesta')
    return redirect('ver_encuesta', encuesta_id=encuesta_id)


def reportes(request):
    if not (request.user.is_authenticated and (request.user.is_superuser or request.user.es_administrador)):
        return redirect('login')

    periodo = request.GET.get('periodo', 'diario')
    today = timezone.now().date()
    if periodo == 'semanal':
        inicio = today - timedelta(days=7)
    elif periodo == 'mensual':
        inicio = today - timedelta(days=30)
    else:
        inicio = today

    informes = (
        Informe.objects.filter(fecha__gte=inicio, fecha__lte=today)
        .values('tema__nombre')
        .annotate(total=Sum('cantidad'))
        .order_by('-total')
    )

    return render(request, 'informes.html', {
        'informes': informes,
        'periodo': periodo,
    })
