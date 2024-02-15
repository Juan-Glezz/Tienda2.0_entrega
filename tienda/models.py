from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils import timezone


# Create your models here.
class Marca(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Marcas"


class Producto(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    unidades = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    vip = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.marca}{self.modelo}'

    class Meta:
        unique_together = ['marca', 'modelo']
        verbose_name_plural = "Productos"


class Cliente(models.Model):
    vip = models.BooleanField(default=False)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, max_length=40)

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name_plural = "Clientes"


class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    user = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    unidades = models.IntegerField()
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0.21)

    def __str__(self):
        return f'{self.user.user.username}{self.fecha}'

    class Meta:
        unique_together = ['fecha', 'producto', 'user']
        verbose_name_plural = "Compras"


class Comentario(models.Model):
    valoracion = models.IntegerField(choices=[(1, '⭐'), (2, '⭐⭐'), (3, '⭐⭐⭐'), (4, '⭐⭐⭐⭐'), (5, '⭐⭐⭐⭐⭐')], blank=True,
                                     null=True)
    comentario = models.TextField(blank=True, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.comentario}-{self.valoracion}'

    class Meta:
        verbose_name_plural = "Comentarios"


class Direccion(models.Model):
    direccion_envio = models.TextField(blank=True, null=True)
    direccion_facturacion = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Direcciones"


class Tarjeta(models.Model):
    nombre_tarjeta = models.CharField(max_length=40, blank=True, null=True)
    TIPO_TARJETA_CHOICES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
    ]
    tipo_tarjeta = models.CharField(max_length=20, choices=TIPO_TARJETA_CHOICES, blank=True, null=True)
    titular_tarjeta = models.CharField(max_length=40, blank=True, null=True)
    caducidad_tarjeta = models.DateField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Tarjetas"
