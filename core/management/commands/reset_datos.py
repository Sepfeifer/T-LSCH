from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Usuario, Tema, Video, Informe
from django.contrib.auth import get_user_model
from datetime import date, timedelta, datetime


class Command(BaseCommand):
    help = 'Reinicia la base de datos con usuarios, temas, videos e informes'

    def handle(self, *args, **options):
        # Eliminar datos antiguos
        Video.objects.all().delete()
        Tema.objects.all().delete()
        Informe.objects.all().delete()
        get_user_model().objects.exclude(is_superuser=True).delete()

        # Crear temas
        temas_creados = {
            "general": Tema.objects.create(nombre="general"),
            "carnet": Tema.objects.create(nombre="carnet"),
            "defunción": Tema.objects.create(nombre="defunción"),
        }

           # Crear usuarios
        User = get_user_model()
        usuarios = [
            {
                "id_rut": "11111111-1",
                "email": "admin@ejemplo.com",
                "nombre": "Admin",
                "apellido": "Principal",
                "correo": "admin@ejemplo.com",
                "rol": "ADMINISTRADOR",
                "password": "admin123",
                "es_administrador": True,
                "es_funcionario": False
            },
            {
                "id_rut": "22222222-2",
                "email": "jgomez@ejemplo.com",
                "nombre": "Juan Gonzalo",
                "apellido": "Gomez Martinez",
                "correo": "jgomez@ejemplo.com",
                "rol": "FUNCIONARIO",
                "password": "func123",
                "es_administrador": False,
                "es_funcionario": True
            },
            {
                "id_rut": "33333333-3",
                "email": "gzapata@ejemplo.com",
                "nombre": "Gabriela",
                "apellido": "Zapata",
                "correo": "gzapata@ejemplo.com",
                "rol": "FUNCIONARIO",
                "password": "func123",
                "es_administrador": False,
                "es_funcionario": True
            },
            {
                "id_rut": "44444444-4",
                "email": "dbastias@ejemplo.com",
                "nombre": "Dominik Chester",
                "apellido": "Bastias Leon",
                "correo": "dbastias@ejemplo.com",
                "rol": "FUNCIONARIO",
                "password": "func123",
                "es_administrador": False,
                "es_funcionario": True
            },
            {
                "id_rut": "55555555-5",
                "email": "mrosas@ejemplo.com",
                "nombre": "Maria",
                "apellido": "Rosas Soto",
                "correo": "mrosas@ejemplo.com",
                "rol": "FUNCIONARIO",
                "password": "func123",
                "es_administrador": False,
                "es_funcionario": True
            },
            {
                "id_rut": "66666666-6",
                "email": "cmarquez@ejemplo.com",
                "nombre": "Carlos",
                "apellido": "Marquez Fuentealba",
                "correo": "cmarquez@ejemplo.com",
                "rol": "FUNCIONARIO",
                "password": "func123",
                "es_administrador": False,
                "es_funcionario": True
            },
        ]

        for u in usuarios:
            User.objects.create_user(
                id_rut=u["id_rut"],
                email=u["email"],
                nombre=u["nombre"],
                apellido=u["apellido"],
                password=u["password"],
                correo=u["correo"],
                rol=u["rol"],
                es_administrador=u["es_administrador"],
                es_funcionario=u["es_funcionario"]
            )

        # Videos crudos (sin normalizar)
        videos_raw = [
                ("Z", "https://www.youtube.com/watch?v=HphdbWoZ21I", "General"),
                ("Perder", "https://www.youtube.com/watch?v=MsQf8h91v8w", "Carnet"),
                ("Pagar", "https://www.youtube.com/watch?v=tS1Ihhe3zj8", "Carnet"),
                ("P", "https://www.youtube.com/watch?v=Ze-pQuFe1ks", "General"),
                ("Olvidar", "https://www.youtube.com/watch?v=IpL5YmxE0Tw", "Carnet"),
                ("O", "https://www.youtube.com/watch?v=JE0zKgmImE8", "General"),
                ("Nombre", "https://www.youtube.com/watch?v=CgBQTAEIDgU", "Carnet"),
                ("N", "https://www.youtube.com/watch?v=Y55jiUCoZ_I", "General"),
                ("M", "https://www.youtube.com/watch?v=xxpPEEs2qZA", "General"),
                ("L", "https://www.youtube.com/watch?v=wGTlzfAMoeA", "General"),
                ("J", "https://www.youtube.com/watch?v=pkNduE43hHc", "General"),
                ("Registro civil", "https://www.youtube.com/watch?v=xxhcOrnDRAw", "Carnet"),
                ("R", "https://www.youtube.com/watch?v=QNRuKxclSEw", "General"),
                ("Q", "https://www.youtube.com/watch?v=hs-iD-y6y2w", "General"),
                ("Porque", "https://www.youtube.com/watch?v=AFnMy-ivQF0", "General"),
                ("Poner Huella", "https://www.youtube.com/watch?v=WTFQ45V20Vs", "Carnet"),
                ("Falta", "https://www.youtube.com/watch?v=nxDw2rAVDAc", "Carnet"),
                ("F", "https://www.youtube.com/watch?v=qFW9z3j58jY", "General"),
                ("Esperar", "https://www.youtube.com/watch?v=xVrnm8rDfW0", "General"),
                ("Enviar", "https://www.youtube.com/watch?v=8D7u9fM0XvY", "General"),
                ("Entregar documento", "https://www.youtube.com/watch?v=ibNcy0rqm5I", "Carnet"),
                ("I", "https://www.youtube.com/watch?v=FPDSdKzdsyU", "General"),
                ("H", "https://www.youtube.com/watch?v=TFK4Oxm7aU0", "General"),
                ("Gmail", "https://www.youtube.com/watch?v=b92ktfCBRK8", "General"),
                ("G", "https://www.youtube.com/watch?v=OGkHWOdE8jY", "General"),
                ("Foto", "https://www.youtube.com/watch?v=CeUEeA0n_jU", "Carnet"),
                ("Firmar aqui", "https://www.youtube.com/watch?v=-Of8Qw6DgmA", "Carnet"),
                ("Falta", "https://www.youtube.com/watch?v=sHvQp3eVI18", "Carnet"),
                ("Cuatro Semanas", "https://www.youtube.com/watch?v=hLt3buFe5J0", "General"),
                ("Cuanto", "https://www.youtube.com/watch?v=A8DRU5EtB0c", "General"),
                ("Comprobante de pago", "https://www.youtube.com/watch?v=D-_vTuHyCqo", "Carnet"),
                ("Como", "https://www.youtube.com/watch?v=vP-X1L-1YDQ", "General"),
                ("Carabineros", "https://www.youtube.com/watch?v=3dhJ6jmcYTA", "General"),
                ("C", "https://www.youtube.com/watch?v=VM7yN15fc6w", "General"),
                ("Entrar a internet", "https://www.youtube.com/watch?v=PW-BtWNbJLs", "General"),
                ("E", "https://www.youtube.com/watch?v=ZV3wR514iCc", "General"),
                ("Dos Semanas", "https://www.youtube.com/watch?v=GcHOW8mnWD0", "General"),
                ("Documento de defunción", "https://www.youtube.com/watch?v=sqKEZMnSzNY", "Defunción"),
                ("Descargar", "https://www.youtube.com/watch?v=r-WTqQLxH1s", "General"),
                ("D", "https://www.youtube.com/watch?v=HOlg7Ag6nZM", "General"),
                ("$3500", "https://www.youtube.com/watch?v=UCY13_BuK8s", "Carnet"),
                ("Buscar", "https://www.youtube.com/watch?v=cfMd8rDuxm8", "General"),
                ("Bloquear Carnet", "https://www.youtube.com/watch?v=g2fUhUUwthU", "Carnet"),
                ("B", "https://www.youtube.com/watch?v=SZCciwKvPz0", "General"),
                ("Ayudar", "https://www.youtube.com/watch?v=aHnc3G84tnY", "General"),
                ("Avisar", "https://www.youtube.com/watch?v=gmQTLWIOhJE", "General"),
                ("Apellido", "https://www.youtube.com/watch?v=FSuZy5WE0Z8", "Carnet"),
                ("Acta_de_nacimiento", "https://www.youtube.com/watch?v=UCNwjnpwH_w", "Defunción"),
                ("acta de nacimiento donde", "https://www.youtube.com/watch?v=Frgs_088lGc", "Defunción"),
                ("A", "https://www.youtube.com/watch?v=W54URsoyZGI", "General"),
                ("Una Semana", "https://www.youtube.com/watch?v=-04G12_1ssA", "General"),
                ("Como estas", "https://youtu.be/EzrS3MJq0kI", "General"),
                ("T", "https://youtu.be/Dp7dVpqtHpk", "General"),
                ("Hola", "https://youtu.be/FtqWE2L9B6g", "General"),
                ("Cual", "https://youtu.be/3K-R2vhWK68", "General"),
                ("diez", "https://youtu.be/NjtLLXPaFEA", "General"),
                ("uno", "https://youtu.be/ZGoqKbemwX0", "General"),
                ("tres", "https://youtu.be/RCtcRXMLrXI", "General"),
                ("siete", "https://youtu.be/Ctetp0Op-bo", "General"),
                ("seis", "https://youtu.be/LBNxeyeGHHU", "General"),
                ("s", "https://youtu.be/Eju4O3jkj-E", "General"),
                ("ocho", "https://youtu.be/Se6po9IS2vw", "General"),
                ("nueve", "https://youtu.be/z0_Qu1icxpg", "General"),
                ("dos", "https://youtu.be/BFelIGOgY6k", "General"),
                ("cuatro", "https://youtu.be/NEFh-Db-WBg", "General"),
                ("cinco", "https://youtu.be/9kxO4Uk47Wg", "General"),
                ("carnet", "https://youtu.be/_KQukB41qXg", "General"),
                ("donde", "https://youtu.be/tOcbcVLtvOU", "General"),
            ]

        # Normalizar nombres
        videos_normalizados = []
        for nombre, url, tema in videos_raw:
            nombre_normalizado = nombre.strip().lower().replace(" ", "_")
            videos_normalizados.append({
                "nombre": nombre_normalizado,
                "url_codigo": url.strip(),
                "tema": tema.strip().lower(),
                "fecha_creacion": datetime.now()
            })

        # Crear los videos y asignar a temas
        for video in videos_normalizados:
            tema_obj = temas_creados.get(video["tema"])
            if not tema_obj:
                self.stdout.write(self.style.ERROR(f"❌ Tema no encontrado: '{video['tema']}' para video '{video['nombre']}'"))
                continue

            nuevo_video = Video.objects.create(
                nombre=video["nombre"],
                url_codigo=video["url_codigo"],
                fecha_creacion=video["fecha_creacion"]
            )
            nuevo_video.temas.set([tema_obj])
            self.stdout.write(self.style.SUCCESS(f"✅ Video creado: {video['nombre']} en tema '{tema_obj.nombre}'"))

        # Informes de ejemplo
        hoy = date.today()
        semana = hoy - timedelta(days=7)
        mes = hoy - timedelta(days=30)

        if "carnet" in temas_creados:
            Informe.objects.create(tema=temas_creados["carnet"], cantidad=5, fecha=hoy)
            Informe.objects.create(tema=temas_creados["carnet"], cantidad=12, fecha=semana)
            Informe.objects.create(tema=temas_creados["carnet"], cantidad=30, fecha=mes)

        self.stdout.write(self.style.SUCCESS("🎉 Base de datos reiniciada con éxito."))