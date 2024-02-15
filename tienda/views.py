from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from .form import PostProducto, CompraForm, RegistroForm, ClienteForm, DireccionesForm, TarjetasForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Sum
from django.db import transaction
from .models import Producto, Cliente, Compra, Marca, Direccion, Tarjeta, Comentario
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
import json


def cliente_existe(user):
    return Cliente.objects.filter(user=user).exists()


class WelcomeView(TemplateView):
    template_name = "tienda/index.html"


class ProductosView(ListView):
    model = Producto
    template_name = 'tienda/producto.html'
    context_object_name = 'Productos'

    @method_decorator(login_required(login_url='/tienda/login/'))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CompraView(ListView):
    model = Producto
    template_name = 'tienda/compra.html'
    context_object_name = 'Productos'


class Post_EditView(UpdateView):
    model = Producto
    template_name = 'tienda/editar.html'
    form_class = PostProducto
    success_url = reverse_lazy('productos')

    @method_decorator(login_required(login_url='/tienda/login/'))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@method_decorator(login_required(login_url='/tienda/login/'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class Post_eliminarView(DeleteView):
    model = Producto

    def get(self, request, pk):
        producto = Producto.objects.filter(pk=pk).delete()
        return redirect('productos')


class Post_Nuevo_View(CreateView):
    model = Producto
    template_name = 'tienda/nuevo.html'
    form_class = PostProducto
    success_url = reverse_lazy('productos')

    @method_decorator(login_required(login_url='/tienda/login/'))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class BuscarProductoListView(ListView):
    model = Producto
    template_name = 'tienda/mostrarBusqueda.html'
    context_object_name = 'Productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get('buscar_post')
        if busqueda:
            queryset = queryset.filter(nombre__icontains=busqueda)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('buscar_post')
        return context


class Log_In_View(LoginView):
    template_name = 'tienda/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        nextURL = self.get_success_url()
        if not nextURL:
            nextURL = 'tienda/'
        return redirect(nextURL)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response


class Log_outView(View):
    def get(self, request):
        logout(request)
        return redirect('welcome')


@method_decorator(login_required, name='dispatch')
class Checkout(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'tienda/checkout.html'
    model = Compra
    form_class = CompraForm
    success_url = reverse_lazy('welcome')

    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = CompraForm()
        comentarios = Compra.objects.filter(producto=producto).order_by('-fecha')
        return render(request, 'tienda/checkout.html', {'form': form, 'producto': producto, 'comentarios': comentarios})

    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        cliente = get_object_or_404(Cliente, user=request.user)
        form = CompraForm(request.POST)
        if form.is_valid():
            unidades = form.cleaned_data['unidades']
            if unidades <= producto.unidades:
                with transaction.atomic():
                    producto.unidades -= unidades
                    producto.save()
                    compra = Compra()
                    compra.producto = producto
                    compra.user = cliente
                    compra.unidades = unidades
                    compra.importe = unidades * producto.precio
                    compra.fecha = timezone.now()
                    compra.save()
                    cliente.saldo -= compra.importe
                    cliente.save()
                return redirect('welcome')
        return render(request, 'tienda/checkout.html', {'form': form, 'producto': producto})


class TopProducto_Views(ListView):
    template_name = 'tienda/informe.html'
    context_object_name = 'topP'

    def get(self, request):
        topP = Producto.objects.annotate(sum_unidades=Sum('compra__unidades'),
                                         sum_importes=Sum('compra__importe')).order_by('-sum_unidades')[:10]
        return render(request, self.template_name, {'topP': topP})


# La función realiza una consulta a la base de datos para obtener los 10 mejores clientes.
# Utilizando Cliente.objects.annotate(gastado=Sum('compra__importe')), se agrega una anotación
# llamada gastado que calcula la suma de los importes de todas las compras realizadas por cada cliente.
# Luego, los resultados se ordenan de forma descendente basándose en el campo gastado. Finalmente, se
# renderiza la plantilla top10mejores.html con los datos de los topClientes.
class topClientes_View(ListView):
    model = Cliente
    template_name = 'tienda/informe.html'
    context_object_name = 'clientes'

    def get_queryset(self):
        return Cliente.objects.annotate(gastado=Sum('compra__importe')).order_by('-gastado')[:10]


# En esta funcion, se obtiene todas las compras realizadas por un usuario mediante el uso de
# la función filter de la clase Compra. Estas compras se ordenan por fecha en orden descendente.
# Luego, se renderiza la plantilla tienda/historialCompras.html y se pasa el resultado de la consulta a compras.
# Esto permitirá que la plantilla acceda a los datos de las compras y los muestre correctamente.
class historial_View(ListView):
    model = Compra
    template_name = 'tienda/informe.html'
    context_object_name = 'compras'
    ordering = '-fecha'

    def get_queryset(self):
        return super().get_queryset().order_by(self.ordering)


class EditarDireccionView(LoginRequiredMixin, UpdateView):
    redirect_field_name = "/tienda/login/"
    model = Direccion
    form_class = DireccionesForm
    template_name = 'tienda/direcciones.html'
    success_url = reverse_lazy('perfil_cliente')

    def get(self, request, *args, **kwargs):
        direccion, created = Direccion.objects.get_or_create(user=request.user)
        form = DireccionesForm(instance=direccion)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        # Obtener el perfil del cliente actual o crear uno nuevo si no existe
        direccion, created = Direccion.objects.get_or_create(user=request.user)
        form = DireccionesForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            return redirect('menu')
        return render(request, self.template_name, {'form': form})


class EditarTarjetaView(LoginRequiredMixin, UpdateView):
    edirect_field_name = "/tienda/login/"
    model = Tarjeta
    form_class = TarjetasForm
    template_name = 'tienda/tarjetas.html'
    success_url = reverse_lazy('perfil_cliente')

    def get(self, request, *args, **kwargs):
        tarjeta, created = Tarjeta.objects.get_or_create(user=request.user)
        form = TarjetasForm(instance=tarjeta)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        tarjeta, created = Tarjeta.objects.get_or_create(user=request.user)
        form = TarjetasForm(request.POST, instance=tarjeta)
        if form.is_valid():
            form.save()
            return redirect('menu')
        return render(request, self.template_name, {'form': form})


class EditarGeneralView(LoginRequiredMixin, UpdateView):
    redirect_field_name = "/tienda/login/"
    model = ClienteForm
    form_class = ClienteForm
    template_name = 'tienda/perfil.html'
    success_url = reverse_lazy('perfil_cliente')

    def get(self, request, *args, **kwargs):
        cliente, created = Cliente.objects.get_or_create(user=request.user)
        form = ClienteForm(instance=cliente)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        cliente, created = Cliente.objects.get_or_create(user=request.user)
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('menu')
        return render(request, self.template_name, {'form': form})


class menuPerfil(TemplateView):
    template_name = 'tienda/menu.html'


class RegistroView(View):
    template_name = 'tienda/registro.html'
    form_class = RegistroForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            cliente = Cliente(user=user, saldo=0, vip=False)
            cliente.save()

            login(request, user)
            return redirect('welcome')
        return render(request, self.template_name, {'form': form})


class ComentarioCreateView(CreateView):
    model = Comentario
    fields = ['valoracion', 'comentario']
    template_name = 'tienda/comentario_create.html'

    def form_valid(self, form):
        form.instance.producto_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('checkout', kwargs={'pk': self.kwargs['pk']})


class ComentarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Comentario
    fields = ['valoracion', 'comentario']
    template_name = 'tienda/comentario_editar.html'

    def get_success_url(self):
        return reverse_lazy('checkout', kwargs={'pk': self.object.producto_id})

    def test_func(self):
        comentario = self.get_object()
        return self.request.user == comentario.user.user


class ComentarioListView(ListView):
    model = Comentario
    template_name = 'tienda/checkout.html'


class AgregarAlCarrito(View):
    def post(self, request, *args, **kwargs):
        producto_id = request.POST.get('producto_id')
        unidades = int(request.POST.get('unidades', 1))

        carrito = request.session.get('carrito', [])
        if carrito:
            carrito = json.loads(carrito)

        carrito.append({
            'producto_id': producto_id,
            'unidades': unidades
        })

        request.session['carrito'] = json.dumps(carrito)
        return redirect('checkout', pk=producto_id)


class VerCarritoView(TemplateView):
    template_name = 'tienda/ver_carrito.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = self.request.session.get('carrito', [])
        if carrito:
            carrito = json.loads(carrito)
            productos = Producto.objects.filter(id__in=[item['producto_id'] for item in carrito])
            for item in carrito:
                producto = productos.get(id=item['producto_id'])
                item['producto'] = producto
                # Calcular el precio total para cada elemento del carrito
                item['precio_total'] = item['unidades'] * producto.precio
        context['carrito'] = carrito
        return context


class CheckoutCarritoView(View):
    template_name = 'tienda/checkout_carrito.html'

    def get(self, request, *args, **kwargs):
        # Obtener el contenido del carrito de la sesión
        carrito = request.session.get('carrito', [])
        if carrito:
            carrito = json.loads(carrito)
            productos = Producto.objects.filter(id__in=[item['producto_id'] for item in carrito])
            for item in carrito:
                producto = productos.get(id=item['producto_id'])
                item['producto'] = producto

        contexto = {'carrito': carrito}
        return render(request, 'tienda/checkout_carrito.html', contexto)

    def post(self, request, *args, **kwargs):
        # Obtener el contenido del carrito de la sesión
        carrito = request.session.get('carrito', [])
        if carrito:
            carrito = json.loads(carrito)
            # Crear una nueva instancia de Compra
            compra = Compra.objects.create(
                user=request.user  # Asignar el usuario actual
            )

            # Agregar los productos del carrito a la compra
            for item in carrito:
                producto = Producto.objects.get(id=item['producto_id'])
                compra.producto_set.create(
                    producto=producto,
                    unidades=item['unidades'],
                    importe=item['unidades'] * producto.precio,
                    iva=0.21
                )
            # Limpiar el carrito después de completar la compra
            request.session['carrito'] = json.dumps([])

            return redirect('checkout_carrito.html')
        else:
            # Si el formulario no es válido, volver a renderizar la página con los errores
            contexto = {'carrito': carrito}
            return render(request, 'tienda/checkout_carrito.html', contexto)
