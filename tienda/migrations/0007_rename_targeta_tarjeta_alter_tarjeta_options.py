# Generated by Django 4.1.13 on 2024-01-23 10:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tienda', '0006_alter_direccion_user_alter_targeta_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Targeta',
            new_name='Tarjeta',
        ),
        migrations.AlterModelOptions(
            name='tarjeta',
            options={'verbose_name_plural': 'Tarjetas'},
        ),
    ]