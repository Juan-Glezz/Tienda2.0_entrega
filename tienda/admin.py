from django.contrib import admin
from .models import Marca,Producto,Cliente,Compra

# Register your models here.
admin.site.register(Marca)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Compra)