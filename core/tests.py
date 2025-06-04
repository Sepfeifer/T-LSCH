from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Tema, Video, Informe


class InformeTests(TestCase):
    def test_traductor_increments_informe(self):
        tema = Tema.objects.create(nombre="rut_signo")
        video = Video.objects.create(nombre="rut", url_codigo="url")
        video.temas.add(tema)

        self.client.post(reverse('traductor_directo'), {'frase': 'rut'})

        informe = Informe.objects.get(tema=tema, fecha=timezone.now().date())
        self.assertEqual(informe.cantidad, 1)
