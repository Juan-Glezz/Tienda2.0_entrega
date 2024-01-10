from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Cliente, Compra
from .form import PostProducto, LoginForm, CompraForm, RegistroForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Sum
from django.db import transaction


# Create your views here.
# una función que devuelve un archivo HTML almacenado en una carpeta específica
# cuando se llama desde una URL específica.
def welcome(request):
    return render(request, 'tienda/index.html', {})


# @login_required: Esto significa que para acceder a la función "productos",
# el usuario debe estar autenticado. Si el usuario
# no está autenticado, se le redirigirá a la URL '/tienda/login/'.
# @staff_member_required: Esto significa que solo los usuarios que tienen el
# permiso de "staff member" podrán acceder a la función "productos".
# Si el usuario no tiene este permiso, recibirá un mensaje de error.


# Esta función recibe un objeto request que contiene la información de la solicitud
# realizada por el cliente, posteriormente se realiza una consulta a la base de datos
# para obtener todos los objetos de la clase Producto. El método filter() devuelve una lista
# de objetos filtrados(En este caso es todo) Y una vez tiene todo los datos los devuelve.

@login_required(login_url='/tienda/login/')
@staff_member_required
def productos(request):
    Productos = Producto.objects.filter();
    return render(request, 'tienda/producto.html', {'Productos': Productos})


# Esta funcion utiliza la función filter() para obtener todos los objetos de la clase Producto
# y almacenarlos en la variable Productos. Luego, se utiliza la función render() para renderizar
# la plantilla tienda/compra.html junto con los productos obtenidos. Estos productos se pasan a
# la plantilla, con el nombre Productos. Esto permite acceder a los productos en la plantilla para mostrarlos.
def compra(request):
    Productos = Producto.objects.filter();
    return render(request, 'tienda/compra.html', {'Productos': Productos})


# Esta funcion tiene el parametro pk, que indica el identificador del Producto que se desea editar,
# une vez hecho esto recupera el objeto Producto basado en el pk proporcionado. Si no se encuentra,
# muestra una página de error 404. Luego si la solicitud es del tipo "POST", se crea una instancia del formulario
# PostProducto utilizando los datos enviados en la solicitud, esta instancia del formulario se asocia con el objeto
# producto que se desea editar. Si el formulario es válido, los cambios se guardan en la base de datos utilizando
# form.save() y se redirige al usuario a la página de productos, en caso de que el formulario no sea válido, se
# renderiza la página de edición nuevamente, pero esta vez con los errores del formulario visibles
# para que el usuario los corrija. Finalmente se renderiza la plantilla tienda/editar.html
@login_required(login_url='/tienda/login/')
@staff_member_required
def post_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = PostProducto(request.POST, instance=producto)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.save()
            return redirect('productos')
    else:
        form = PostProducto(instance=producto)
    return render(request, 'tienda/editar.html', {'form': form, 'pk': pk})


# Esta función toma los argumentos request y pk. El pk es la clave primaria del producto que
# se va a eliminar, se busca el producto en la base de datos usando su clave primaria pk y
# se elimina usando el método delete() y lo elimina de la base de datos. Una vez eliminado,
# redirecciona al usuario a la página de productos
@login_required(login_url='/tienda/login/')
@staff_member_required
def post_eliminar(request, pk):
    producto = Producto.objects.filter(pk=pk).delete()
    return redirect('productos')


# Esta funcion hace que cuando se realiza una solicitud POST con datos válidos en el formulario
# PostProducto, se guarda en la base de datos y se redirige al usuario a la página de productos.
@login_required(login_url='/tienda/login/')
@staff_member_required
def post_nuevo(request):
    if request.method == 'POST':
        form = PostProducto(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = PostProducto()

    return render(request, 'tienda/nuevo.html', {'form': form})


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
def log_in(request):
    if request.user.is_authenticated:
        return redirect('compra')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            rNext = request.GET.get('next')
            if rNext is None:
                rNext = '/tienda'
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(rNext)
            else:
                form.add_error(None, "Nombre de usuario o contraseña no válida")
                return render(request, "tienda/login.html", {"form": form})

    else:
        form = LoginForm()

    return render(request, "tienda/login.html", {"form": form})


# Este código es una función llamada log_out que se encarga de cerrar la sesión de un usuario.
# Primero, se llama a la función logout pasándole el objeto request, lo cual desloguea al
# usuario actual. Luego, se redirige al usuario a la página de bienvenida utilizando la función redirect
# pasándole como argumento el nombre de la ruta welcome.
def log_out(request):
    logout(request)
    return redirect('welcome')


# El código es una función de checkout que recibe una solicitud (request) y un pk como parámetros,
# lo que hace esta función en si es, tomar los datos de un producto y un cliente, y si la solicitud
# es de tipo POST, se valida un formulario de compra. Si el formulario es válido, se crean registros
# de compra relacionados con el cliente y el producto, se calculan las variables y
# se actualizan las cantidades del producto y el saldo del cliente. Finalmente, se redirige a la página
# de bienvenida. Si la solicitud no es de tipo POST, se renderiza un formulario de compra.
@transaction.atomic
@login_required(login_url='/tienda/login/')
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
@login_required(login_url='/tienda/login/')
@staff_member_required
def topProductos(request):
    topP = Producto.objects.annotate(sum_unidades=Sum('compra__unidades'),
                                     sum_importes=Sum('compra__importe')).order_by('-sum_unidades')[:10]
    return render(request, 'tienda/informe.html', {'topP': topP})


# La función, realiza una consulta a la base de datos para obtener los 10 mejores clientes.
# Utilizando Cliente.objects.annotate(gastado=Sum('compra__importe')), se agrega una anotación
# llamada gastado que calcula la suma de los importes de todas las compras realizadas por cada cliente.
# Luego, los resultados se ordenan de forma descendente basándose en el campo gastado. Finalmente, se
# renderiza la plantilla top10mejores.html con los datos de los topClientes.
@login_required(login_url='/tienda/login/')
@staff_member_required
def topClientes(request):
    clientes = Cliente.objects.annotate(gastado=Sum('compra__importe')).order_by('-gastado')[:10]
    return render(request, 'tienda/informe.html', {'clientes': clientes})


# En esta funcion, se obtiene todas las compras realizadas por un usuario mediante el uso de
# la función filter de la clase Compra. Estas compras se ordenan por fecha en orden descendente.
# Luego, se renderiza la plantilla tienda/historialCompras.html y se pasa el resultado de la consulta a compras.
# Esto permitirá que la plantilla acceda a los datos de las compras y los muestre correctamente.
@login_required(login_url='/tienda/login/')
@staff_member_required
def historial(request):
    compras = Compra.objects.all().order_by('-fecha')
    return render(request, 'tienda/informe.html', {'compras': compras})



