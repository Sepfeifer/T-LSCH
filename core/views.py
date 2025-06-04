import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail  # ← AÑADIDO
from django.conf import settings         # ← AÑADIDO
from .models import Usuario, Video, Tema, Encuesta, Opcion, Tramite
from .forms import VideoForm
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from .services.spacy_translator import  translate_to_lsch
from .services.spacy_extractor import extract_keywords_spacy
from .services.synonym_service import get_synonyms

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


def usuario_consulta(request):
    """
    Vista pública donde el usuario sordo-mudo envía su texto de consulta.
    - Si es GET, muestra el formulario.
    - Si es POST, lee 'frase' del formulario, crea un Tramite(frase_original=…) y redirige
      a la página de esa misma consulta para ver playlist+encuesta.
    """
    if request.method == "POST":
        texto = request.POST.get("frase", "").strip()
        if texto:
            tramite = Tramite.objects.create(frase_original=texto)
            return redirect('ver_encuesta_usuario', tramite_id=tramite.id)

    return render(request, "usuario/consulta.html")


def traductor(request):
    """
    Vista que el funcionario usa para:
    - Mostrar la última consulta recibida (si existe).
    - Aceptar la respuesta en texto (POST) para generar playlist.
    - Botón “Refrescar” para recargar y verificar nueva consulta.
    """
    # 1) Recuperar el trámite más reciente (si hay) que aún no tenga encuesta creada.
    #    De este modo, el funcionario ve siempre el último que falta atención.
    ultimo_tramite = Tramite.objects.order_by('-creado_en').first()
    frase = ""
    playlist = []
    matches = {}

    if ultimo_tramite:
        frase = ultimo_tramite.frase_original

        if request.method == "POST":
            # Si llega un POST de “Generar Traducción”
            texto_respuesta = request.POST.get("frase_traductor", "").strip()
            if texto_respuesta:
                # Extraer tokens / palabras para buscar videos
                tokens = []
                for m in re.finditer(r'"([^"]+)"|(\S+)', texto_respuesta):
                    if m.group(1) is not None:
                        # Dentro de comillas → deletrear
                        for ch in m.group(1):
                            if ch.strip():
                                tokens.append(ch.lower())
                    else:
                        tokens.append(m.group(2).lower())

                # Construir playlist en el mismo orden
                lista_videos = []
                for token in tokens:
                    # 1) Buscar video por nombre exacto o parcial
                    video = Video.objects.filter(nombre__iexact=token).first() \
                            or Video.objects.filter(nombre__icontains=token).first()
                    # 2) Si no hay, buscar sinónimo
                    if not video:
                        for syn in get_synonyms(token):
                            video = Video.objects.filter(nombre__icontains=syn).first()
                            if video:
                                break
                    # 3) Si encuentra, convertir a embed o URL directa
                    if video:
                        url = video.url_codigo.strip()
                        if "youtube.com" in url or "youtu.be" in url:
                            video_id = None
                            if "watch?v=" in url:
                                video_id = url.split("watch?v=")[1].split("&")[0]
                            elif "youtu.be/" in url:
                                video_id = url.split("youtu.be/")[1].split("?")[0]
                            embed = f"https://www.youtube.com/embed/{video_id}?enablejsapi=1&autoplay=1" if video_id else url
                            lista_videos.append({
                                "titulo": video.nombre,
                                "url": embed,
                                "is_youtube": True
                            })
                        else:
                            lista_videos.append({
                                "titulo": video.nombre,
                                "url": video.url_codigo,
                                "is_youtube": False
                            })
                        # Guardar coincidencia para mostrar en lista
                        matches[token] = video.nombre

                # 4) Guardar playlist en el propio trámite
                ultimo_tramite.playlist = lista_videos
                ultimo_tramite.save()

                # NOTA: NO REDIRIGIMOS aquí; el funcionario se queda en la misma página.
                # Al recargar manualmente, verá confirmación o lista de coincidencias.

    context = {
        "frase": frase,
        "playlist": ultimo_tramite.playlist if ultimo_tramite else [],
        "matches": matches,
        "tramite": ultimo_tramite
    }
    return render(request, "funcionario/traductor.html", context)


def crear_encuesta(request, tramite_id):
    """
    El funcionario crea la encuesta para el trámite indicado.
    - Si POST, recoge 'encuestaPregunta' y 'opcion'[] del formulario,
      genera el objeto Encuesta y sus Opciones.
    - NO redirige al usuario final; se queda en la pantalla de funcionario.
    """
    tramite = get_object_or_404(Tramite, id=tramite_id)

    if request.method == "POST":
        pregunta = request.POST.get('encuestaPregunta', "").strip()
        opciones = [texto.strip() for texto in request.POST.getlist('opcion') if texto.strip()]
        if pregunta and len(opciones) >= 2:
            # 1) Crear la encuesta
            encuesta = Encuesta.objects.create(pregunta=pregunta)
            # 2) Crear cada opción
            for texto in opciones:
                Opcion.objects.create(encuesta=encuesta, texto=texto)
            # 3) Asociar la encuesta al trámite
            tramite.encuesta = encuesta
            tramite.save()
            # Quedarse en la misma página de traductor para ese trámite
            return redirect('traductor')

    # Si no es POST o faltan datos, regresar al traductor igualmente
    return redirect('traductor')


def ver_encuesta(request, tramite_id):
    """
    Vista pública para que el usuario sordo-mudo vea la playlist + encuesta.
    - Si la encuesta NO existe aún, solo muestra mensaje de “espera”. 
    - Solo si existe encuesta Y playlist, permite reproducir videos y votar.
    """
    tramite = get_object_or_404(Tramite, id=tramite_id)
    encuesta = tramite.encuesta  # Puede ser None si aún no se creó
    playlist = tramite.playlist if (encuesta and tramite.playlist) else []  # Solo mostrar playlist si la encuesta existe

    return render(request, "usuario/ver_encuesta.html", {
        "tramite": tramite,
        "playlist": playlist,
        "encuesta": encuesta,
    })


def responder_encuesta(request, tramite_id):
    """
    Procesa la respuesta del usuario a la encuesta.
    - Si es POST, incrementa el conteo de la opción elegida.
    - Luego redirige a usuario_consulta para que el usuario inicie nuevo trámite.
    """
    if request.method == "POST":
        # El formulario envía 'opcion_sel' con el id de la opción
        opcion_id = int(request.POST.get('opcion_sel'))
        opcion = get_object_or_404(Opcion, id=opcion_id, encuesta__tramites__id=tramite_id)
        opcion.votos += 1
        opcion.save()
        # Después de votar, volvemos a la página de envío de consulta (nueva consulta)
        return redirect('usuario_consulta')
    return redirect('ver_encuesta_usuario', tramite_id=tramite_id)

