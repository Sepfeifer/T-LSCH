import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail  # ← AÑADIDO
from django.conf import settings         # ← AÑADIDO
from .models import Usuario, Video, Tema, Encuesta, Opcion, Tramite, MissingVideoReport
from .forms import VideoForm
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from .services.spacy_translator import  translate_to_lsch
from .services.spacy_extractor import extract_keywords_spacy
from .services import informe_service
from django.template.loader import get_template, render_to_string
from django.utils.dateparse import parse_date
import pandas as pd
import io
from core.services.informe_service import obtener_totales
from xhtml2pdf import pisa
from core.services.synonym_service import get_synonyms
from collections import OrderedDict
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages



def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return None
    return result.getvalue()



def es_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'es_administrador', False))

def es_funcionario(user):
    return user.is_authenticated and getattr(user, 'es_funcionario', False)


# Login
def login_view(request):
    # Si ya está autenticado, redirige según rol:
    if request.user.is_authenticated:
        if es_admin(request.user):
            return redirect('vista_admin')
        return redirect('vista_funcionario')

    # Si es GET, limpiamos cualquier mensaje previo y mostramos el formulario
    if request.method == 'GET':
        # Iterar el storage vacía todos los mensajes existentes
        list(messages.get_messages(request))
        return render(request, 'login/login.html')

    # Si es POST, chequea credenciales
    run = request.POST.get('run')
    password = request.POST.get('password')
    user = authenticate(request, username=run, password=password)

    if user is not None:
        login(request, user)
        # Después de loguearse, redirige según rol:
        if es_admin(user):
            return redirect('vista_admin')
        return redirect('vista_funcionario')
    else:
        messages.error(request, 'RUN o contraseña incorrectos')
        # Re-render con el run para que no lo pierda el usuario
        return render(request, 'login/login.html', {'run': run})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def vista_funcionario(request):
    # Ya no forzamos que el usuario tenga es_funcionario:
    # simplemente mostramos la plantilla a cualquier usuario logueado
    return render(request, 'vista_funcionario.html')


@login_required
def vista_admin(request):
    # Mantenemos la comprobación de solo administrador
    if not (request.user.is_superuser or getattr(request.user, 'es_administrador', False)):
        return redirect('login')
    return render(request, 'vista_admin.html')


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
    Vista pública donde el usuario sordo envía su texto de consulta.
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



@login_required
def traductor(request):
    ultimo_tramite = Tramite.objects.order_by('-creado_en').first()
    matches = OrderedDict()  # Mantiene el orden original
    playlist = []

    if request.method == "POST":
        texto_respuesta = request.POST.get("frase_traductor", "").strip()
        tokens = []
        deletreados = {}

        # 1. Deletrear palabras entre comillas
        for match in re.finditer(r'"([^"]+)"', texto_respuesta):
            palabra = match.group(1)
            letras = [c.lower() for c in palabra if c.isalpha()]
            tokens.extend(letras)
            deletreados[palabra.lower()] = [l.upper() for l in letras]

        # 2. Limpiar texto
        texto_limpio = re.sub(r'[¿?¡!.,;:\n\r]', '', texto_respuesta.lower())
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio.strip())

        # 3. Extraer keywords con spaCy
        keywords = extract_keywords_spacy(texto_limpio)
        tokens_spacy = [k.strip().replace(" ", "_").lower() for k in keywords]
        tokens.extend(tokens_spacy)

        # 4. Eliminar sub-palabras si ya hay multi-palabras
        compuestos = [t for t in tokens if "_" in t]
        simples = [
            t for t in tokens
            if "_" not in t and not any(t in c.split("_") for c in compuestos)
        ]
        tokens = compuestos + simples

        # 5. Buscar videos por cada token
        for token in tokens:
            token_limpio = token.strip().lower()
            if not token_limpio:
                continue

            # Ignorar deletreos tipo G-A-B-R-I-E-L-A
            if "-" in token and all(len(p) == 1 for p in token.split("-")):
                continue

            # Ignorar números puros, ya fueron convertidos a palabras
            if token_limpio.isdigit():
                continue

            token_busqueda = token_limpio.upper() if len(token_limpio) == 1 else token_limpio
            video = Video.objects.filter(nombre__iexact=token_busqueda).first()

            if not video:
                for syn in get_synonyms(token_busqueda):
                    video = Video.objects.filter(nombre__iexact=syn.lower()).first()
                    if video:
                        break

            if video:
                url = video.url_codigo.strip()
                if "watch?v=" in url or "youtu.be" in url:
                    vid = (
                        url.split("watch?v=")[-1]
                        if "watch?v=" in url
                        else url.split("youtu.be/")[-1]
                    ).split("&")[0]
                    embed = f"https://www.youtube.com/embed/{vid}?enablejsapi=1&autoplay=1"
                    playlist.append({
                        "titulo": token,
                        "url": embed,
                        "is_youtube": True
                    })
                else:
                    playlist.append({
                        "titulo": token,
                        "url": url,
                        "is_youtube": False
                    })
                matches[token] = video.nombre
            else:
                matches[token] = f"{token_busqueda} (no encontrado)"
                playlist.append({
                    "titulo": token_busqueda,
                    "url": "#",
                    "is_youtube": False,
                    "error": True
                })

        # 6. Mostrar deletreos al final
        for palabra, letras in deletreados.items():
            matches[palabra] = " → ".join(letras)

        # 7. Guardar en el trámite
        if ultimo_tramite:
            ultimo_tramite.playlist = playlist
            ultimo_tramite.save()

    context = {
        "frase": ultimo_tramite.frase_original if ultimo_tramite else "",
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
    Vista pública para que el usuario sordo vea la playlist + encuesta.
    - Si la encuesta NO existe aún, solo muestra mensaje de “espera”. 
    - Solo si existe encuesta Y playlist, permite reproducir videos y votar.
    """
    tramite = get_object_or_404(Tramite, id=tramite_id)
    encuesta = tramite.encuesta  # Puede ser None si aún no se creó
    playlist = (
        tramite.playlist if (encuesta and tramite.playlist) else []
    )  # Solo mostrar playlist si la encuesta existe

    if playlist:
        for item in playlist:
            video = Video.objects.filter(nombre=item.get("titulo")).first()
            if video:
                obtener_totales(video)

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


def informe_list(request):
    desde_txt = request.GET.get('desde')
    hasta_txt = request.GET.get('hasta')
    desde = parse_date(desde_txt) if desde_txt else None
    hasta = parse_date(hasta_txt) if hasta_txt else None
    datos = informe_service.obtener_totales(desde, hasta)
    datos_render = {k: v.to_dict(orient='records') for k, v in datos.items()}

    if 'excel' in request.GET:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for nombre, df in datos.items():
                df.to_excel(writer, sheet_name=nombre, index=False)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="informes.xlsx"'
        return response

    if 'pdf' in request.GET:
        pdf_content = render_to_pdf('informe_pdf.html', {'datos': datos_render})
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="informes.pdf"'
        return response

    return render(request, 'informes.html', {'datos': datos_render, 'desde': desde_txt, 'hasta': hasta_txt})


def generar_pdf(request):
    desde_txt = request.GET.get('desde')
    hasta_txt = request.GET.get('hasta')
    desde = parse_date(desde_txt) if desde_txt else None
    hasta = parse_date(hasta_txt) if hasta_txt else None
    datos = informe_service.obtener_totales(desde, hasta)
    datos_render = {k: v.to_dict(orient='records') for k, v in datos.items()}
    pdf_content = render_to_pdf('informe_pdf.html', {'datos': datos_render})
    return HttpResponse(pdf_content, content_type='application/pdf')

@login_required
@user_passes_test(es_admin)
def notificaciones(request):
    # sólo pendientes
    reportes = MissingVideoReport.objects.filter(resolved=False).order_by('-created_at')
    return render(request, 'notificaciones.html', {
        'reportes': reportes,
    })

@login_required
@user_passes_test(es_admin)
def marcar_resuelto(request, pk):
    reporte = get_object_or_404(MissingVideoReport, pk=pk)
    reporte.resolved = True
    reporte.save()
    return redirect('notificaciones')

@login_required
def reportar_video_faltante(request):
    keyword = request.GET.get('keyword')
    if keyword:
        # Evitamos duplicados abiertos
        existe = MissingVideoReport.objects.filter(keyword=keyword, resolved=False).exists()
        if not existe:
            MissingVideoReport.objects.create(
                keyword=keyword,
                reported_by=request.user
            )
            messages.success(request, f"Se ha reportado falta de vídeo para “{keyword}”.")
        else:
            messages.info(request, f"Ya existe un reporte pendiente para “{keyword}”.")
    return redirect(request.META.get('HTTP_REFERER','/'))