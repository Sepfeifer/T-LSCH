import pandas as pd
from django.utils import timezone
from ..models import Tramite, Video


def obtener_totales(desde=None, hasta=None):
    """Devuelve conteos diario, semanal y mensual de Tramites por tema."""
    qs = Tramite.objects.all()
    if desde:
        qs = qs.filter(creado_en__date__gte=desde)
    if hasta:
        qs = qs.filter(creado_en__date__lte=hasta)

    registros = []
    for tramite in qs:
        fecha = timezone.localtime(tramite.creado_en).date()
        playlist = tramite.playlist if isinstance(tramite.playlist, list) else []
        for item in playlist:
            nombre = item.get("titulo")
            if not nombre:
                continue
            try:
                video = Video.objects.get(nombre=nombre)
            except Video.DoesNotExist:
                continue
            for tema in video.temas.all():
                registros.append({"tema": tema.nombre, "fecha": fecha})

    if not registros:
        vacio = pd.DataFrame(columns=["tema", "fecha", "total"])
        return {"diario": vacio, "semanal": vacio, "mensual": vacio}

    df = pd.DataFrame(registros)
    df["semana"] = df["fecha"].apply(lambda d: f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}")
    df["mes"] = df["fecha"].apply(lambda d: d.strftime("%Y-%m"))

    diario = df.groupby(["tema", "fecha"]).size().reset_index(name="total")
    semanal = df.groupby(["tema", "semana"]).size().reset_index(name="total")
    mensual = df.groupby(["tema", "mes"]).size().reset_index(name="total")
    return {"diario": diario, "semanal": semanal, "mensual": mensual}
