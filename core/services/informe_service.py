from datetime import date

from django.db.models import F

from core.models import Informe


def registrar_video(video):
    """Actualiza o crea un Informe por tema para la fecha actual."""
    hoy = date.today()
    for tema in video.temas.all():
        informe, _ = Informe.objects.get_or_create(
            tema=tema,
            fecha=hoy,
            defaults={"contador": 0},
        )
        informe.contador = F("contador") + 1
        informe.save()
