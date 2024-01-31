from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from .form import PostProducto, LoginForm, CompraForm, RegistroForm, ClienteForm, DireccionesForm, TarjetasForm, \
    ComentarioForm
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


def cliente_existe(user):
    return Cliente.objects.filter(user=user).exists()


# Create your views here.
# una función que devuelve un archivo HTML almacenado en una carpeta específica
# cuando se llama desde una URL específica.
class WelcomeView(TemplateView):
    template_name = "tienda/index.html"


# @login_required: Esto significa que para acceder a la función "productos",
# el usuario debe estar autenticado. Si el usuario
# no está autenticado, se le redirigirá a la URL '/tienda/login/'.
# @staff_member_required: Esto significa que solo los usuarios que tienen el
# permiso de "staff member" podrán acceder a la función "productos".
# Si el usuario no tiene este permiso, recibirá un mensaje de error.


# Esta función recibe un objeto request que contiene la información de la solicitud
# realizada por el cliente, posteriormente se realiza una consulta a la base de datos
# para obtener todos los objetos de la clase Producto. El método filter() devuelve una lista
# de objetos filtrados(En este caso es


class ProductosView(ListView):
    model = Producto
    template_name = 'tienda/producto.html'
    context_object_name = 'Productos'

    @method_decorator(login_required(login_url='/tienda/login/'))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# Esta funcion utiliza la función filter() para obtener todos los objetos de la clase Producto
# y almacenarlos en la variable Productos. Luego, se utiliza la función render() para renderizar
# la plantilla tienda/compra.html junto con los productos obtenidos. Estos productos se pasan a
# la plantilla, con el nombre Productos. Esto permite acceder a los productos en la plantilla para mostrarlos.
class CompraView(ListView):
    model = Producto
    template_name = 'tienda/compra.html'
    context_object_name = 'Productos'


# Esta funcion tiene el parametro pk, que indica el identificador del Producto que se desea editar,
# une vez hecho esto recupera el objeto Producto basado en el pk proporcionado. Si no se encuentra,
# muestra una página de error 404. Luego si la solicitud es del tipo "POST", se crea una instancia del formulario
# PostProducto utilizando los datos enviados en la solicitud, esta instancia del formulario se asocia con el objeto
# producto que se desea editar. Si el formulario es válido, los cambios se guardan en la base de datos utilizando
# form.save() y se redirige al usuario a la página de productos, en caso de que el formulario no sea válido, se
# renderiza la página de edición nuevamente, pero esta vez con los errores del formulario visibles
# para que el usuario los corrija. Finalmente, se renderiza la plantilla tienda/editar.html
class Post_EditView(UpdateView):
    model = Producto
    template_name = 'tienda/editar.html'
    form_class = PostProducto
    success_url = reverse_lazy('productos')

    @method_decorator(login_required(login_url='/tienda/login/'))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# Esta función toma los argumentos request y pk. El pk es la clave primaria del producto que
# se va a eliminar, se busca el producto en la base de datos usando su clave primaria pk y
# se elimina usando el método delete() y lo elimina de la base de datos. Una vez eliminado,
# redirecciona al usuario a la página de productos
@method_decorator(login_required(login_url='/tienda/login/'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class Post_eliminarView(DeleteView):
    model = Producto

    def get(self, request, pk):
        producto = Producto.objects.filter(pk=pk).delete()
        return redirect('productos')


# Esta funcion hace que cuando se realiza una solicitud POST con datos válidos en el formulario
# PostProducto, se guarda en la base de datos y se redirige al usuario a la página de productos.
class Post_Nuevo_View(CreateView):
    model = Producto
    template_name = 'tienda/nuevo.html'
    form_class = PostProducto
    success_url = reverse_lazy('productos')

    @method_decorator(login_required(login_url='/tienda/login/'))
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# Obtiene el valor del parámetro "buscar_post" de la solicitud utilizando el método GET, con ello
# filtra los objetos de la clase Producto en la base de datos. En este caso, los productos se
# filtran por su nombre y se obtienen aquellos cuyo nombre coincide con el criterio de búsqueda.
# Carga su html correspondiente y pasa los productos obtenidos y el término de búsqueda como variables y finalmente lo renderiza.
def post_buscar(request):
    busqueda = request.GET.get("buscar_post")
    Productos = Producto.objects.filter(nombre=busqueda)
    return render(request, 'tienda/mostrarBusqueda.html', {'Productos': Productos, "busqueda": busqueda})


# Este código define la función log_in que recibe un objeto request como parámetro. El objeto request
#  contiene información sobre la solicitud. Esto realiza varias comprobaciones con el inicio de sesión
# de un usuario: redirecciona al usuario a la página de compra si ya está iniciado sesión, verifica
# si la solicitud es de tipo POST, crea un formulario de inicio de sesión utilizando los datos recibidos
# valida el formulario, obtiene el nombre de usuario y la contraseña ingresados, obtiene el destino de
# redirección, autentica al usuario verificando su nombre de usuario y contraseña, inicia sesión si
# el usuario es válido, muestra un mensaje de error si el usuario no es válido, crea un formulario
# vacío si la solicitud no es de tipo POST y finalmente renderiza la página de inicio de sesión con el formulario correspondiente.
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


# Este código es una función llamada log_out que se encarga de cerrar la sesión de un usuario.
# Primero, se llama a la función logout pasándole el objeto request, lo cual desloguea al
# usuario actual. Luego, se redirige al usuario a la página de bienvenida utilizando la función redirect
# pasándole como argumento el nombre de la ruta welcome.
class Log_outView(View):
    def get(self, request):
        logout(request)
        return redirect('welcome')


# El código es una función de checkout que recibe una solicitud (request) y un pk como parámetros,
# lo que hace esta función en si es, tomar los datos de un producto y un cliente, y si la solicitud
# es de tipo POST, se valida un formulario de compra. Si el formulario es válido, se crean registros
# de compra relacionados con el cliente y el producto, se calculan las variables y
# se actualizan las cantidades del producto y el saldo del cliente. Finalmente, se redirige a la página
# de bienvenida. Si la solicitud no es de tipo POST, se renderiza un formulario de compra.
@transaction.atomic
@login_required(login_url='/tienda/tienda/login/')
def checkout(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    cliente = get_object_or_404(Cliente, user=request.user)
    if request.method == "POST":
        form = CompraForm(request.POST)
        if form.is_valid():
            unidades = form.cleaned_data['unidades']
            if unidades <= producto.unidades:
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
    form = CompraForm()
    return render(request, 'tienda/checkout.html', {'form': form, 'producto': producto})


# Para acceder a esta funcion, el usuario debe haber iniciado sesión y ser miembro del personal.
# La variable productos recupera los objetos de la clase Producto y los ordena según la cantidad
# de compras que han tenido en orden descendente y se seleccionan los primeros 10 productos de la
# lista. Una vez terminado eso, devuelve una respuesta renderizando el template tienda/top10Compras.html
# y pasando la variable productos para poder acceder a ellos en la plantilla.
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


class ValorarProductoView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    template_name = 'tienda/valorar_producto.html'
    model = Comentario
    form_class = ComentarioForm
    success_url = reverse_lazy('comentarios_producto')

    def form_valid(self, form):
        compra_id = self.kwargs['pk']
        compra = get_object_or_404(Compra, id=compra_id)
        producto = compra.producto  # Obtén el producto asociado a la compra
        form.instance.user = self.request.user
        form.instance.producto = producto
        form.instance.fecha_creacion = timezone.now()
        form.instance.fecha_actualizacion = timezone.now()
        return super().form_valid(form)

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs, ):
        context = super().get_context_data(**kwargs)
        producto_pk = self.kwargs['pk']
        context['producto'] = Producto.objects.get(pk=producto_pk)
        return context


class MostrarComentariosView(LoginRequiredMixin, ListView):
    model = Comentario
    template_name = 'tienda/comentarios_producto.html'

    def get_queryset(self):
        filter

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class EditarComentarioView(LoginRequiredMixin, UpdateView):
    model = Comentario
    template_name = 'templates/tienda/editar_comentario.html'
    form_class = ComentarioForm

    def form_valid(self, form):
        nextURL = self.get_success_url()
        if not nextURL:
            nextURL = 'tienda/'
        return redirect(nextURL)

    def dispatch(self, request, *args, **kwargs):
        objeto = self.get_object()
        if request.user != objeto.usuario:
            return redirect('checkout', producto_id=objeto.producto.id)
        return super().dispatch(request, *args, **kwargs)
