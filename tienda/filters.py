import django_filters
from .models import Marca, Producto


class filtroMarca(django_filters.FilterSet):
    marca = django_filters.ChoiceFilter(choices=Marca.objects.values_list("id", "nombre"), empty_label='Todo')

    class Meta:
        model = Producto
        fields = ['marca']
