# Generated by Django 5.2 on 2025-06-12 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_MissingVideoRepor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='informe',
            old_name='contador',
            new_name='cantidad',
        ),
    ]
