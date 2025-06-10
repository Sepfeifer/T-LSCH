import pandas as pd
from datetime import datetime, date
from django.utils import timezone

from ..models import Tramite, Video


def convertir_fecha(valor):
    """Convierte a objeto date si es str, datetime o date."""
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor).date()
        except ValueError:
            return None
    elif isinstance(valor, datetime):
        return valor.date()
    elif isinstance(valor, date):
        return valor
    return None


def obtener_totales(desde=None, hasta=None):
    """Devuelve conteos diario, semanal y mensual de reproducciones por tema."""
    # 1. Normalizar fechas de filtro
    desde = convertir_fecha(desde)
    hasta = convertir_fecha(hasta)

    # 2. Filtrar Tramites
    qs = Tramite.objects.all()
    if desde:
        qs = qs.filter(creado_en__date__gte=desde)
    if hasta:
        qs = qs.filter(creado_en__date__lte=hasta)

    # 3. Precargar todos los videos y sus temas para evitar consultas repetidas
    videos = Video.objects.prefetch_related('temas').all()
    video_temas = {v.nombre: [t.nombre for t in v.temas.all()] for v in videos}

    # 4. Construir lista de registros (tema, fecha) por cada reproducción en playlist
    registros = []
    for tramite in qs:
        fecha = timezone.localtime(tramite.creado_en).date()
        playlist = tramite.playlist if isinstance(tramite.playlist, list) else []
        for item in playlist:
            nombre = item.get("titulo")
            if not nombre:
                continue
            temas = video_temas.get(nombre)
            if not temas:
                continue
            for tema_nombre in temas:
                registros.append({"tema": tema_nombre, "fecha": fecha})

    # 5. Convertir a DataFrame y agrupar
    if not registros:
        vacio = pd.DataFrame(columns=["tema", "fecha", "total"])
        return {"diario": vacio, "semanal": vacio, "mensual": vacio}

    df = pd.DataFrame(registros)
    # Semana en formato YYYY-Www
    df['semana'] = df['fecha'].apply(lambda d: f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}")
    # Mes en formato YYYY-MM
    df['mes'] = df['fecha'].apply(lambda d: d.strftime("%Y-%m"))

    diario = df.groupby(["tema", "fecha"]).size().reset_index(name="total")
    semanal = df.groupby(["tema", "semana"]).size().reset_index(name="total")
    mensual = df.groupby(["tema", "mes"]).size().reset_index(name="total")

    return {"diario": diario, "semanal": semanal, "mensual": mensual}
