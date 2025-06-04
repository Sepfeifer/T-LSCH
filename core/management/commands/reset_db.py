from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from core.models import Tema, Informe
import datetime

class Command(BaseCommand):
    help = "Flush DB and load sample data"

    def handle(self, *args, **options):
        call_command('flush', interactive=False)
        call_command('migrate', interactive=False)

        User = get_user_model()

        # Admin users
        admin1 = User.objects.create_superuser(
            id_rut="111111111",
            email="admin1@example.com",
            nombre="admin",
            apellido="admin",
            password="123"
        )
        admin1.seg_nombre = "admin"
        admin1.apellido_m = "admin"
        admin1.es_administrador = True
        admin1.save()

        admin2 = User.objects.create_superuser(
            id_rut="222222222",
            email="admin2@example.com",
            nombre="admin",
            apellido="admin",
            password="123"
        )
        admin2.seg_nombre = "admin"
        admin2.apellido_m = "admin"
        admin2.es_administrador = True
        admin2.save()

        # Sample funcionarios
        User.objects.create_user(
            id_rut="333333333",
            email="func1@example.com",
            nombre="func",
            apellido="uno",
            password="123",
            seg_nombre="func",
            apellido_m="uno",
            rol="funcionario",
            es_funcionario=True
        )

        User.objects.create_user(
            id_rut="444444444",
            email="func2@example.com",
            nombre="func",
            apellido="dos",
            password="123",
            seg_nombre="func",
            apellido_m="dos",
            rol="funcionario",
            es_funcionario=True
        )

        # Temas
        saludos = Tema.objects.create(nombre="saludos")
        carnet = Tema.objects.create(nombre="carnet")
        defuncion = Tema.objects.create(nombre="defuncion")

        today = datetime.date.today()
        Informe.objects.create(tema=carnet, fecha=today, cantidad=20)
        Informe.objects.create(tema=defuncion, fecha=today, cantidad=10)

        self.stdout.write(self.style.SUCCESS('Base de datos reiniciada con datos de ejemplo.'))

