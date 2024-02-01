from .models import Producto, Compra, Cliente, Tarjeta, Direccion, Comentario
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Es un formulario basado en el modelo de Producto. El formulario tiene los campos nombre, modelo, unidades, precio, vip y marca.

# El formulario se utiliza para crear o actualizar instancias del modelo Producto. Al especificar el modelo en la propiedad model
# de la clase Meta, se le indica al formulario que utilice ese modelo como base para las operaciones de creación o actualización.

# Los campos definidos en el atributo fields determinan qué campos del modelo Producto se mostrarán en el formulario.
class PostProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'modelo', 'unidades', 'precio', 'vip', 'marca']


# Es un formulario basado en el modelo de Producto. El formulario tiene los campos nombre, modelo, unidades, precio, vip y marca.
# El formulario se utiliza para crear o actualizar instancias del modelo Producto. Al especificar el modelo en la propiedad model
# de la clase Meta, se le indica al formulario que utilice ese modelo como base para las operaciones de creación o actualización.
# Los campos definidos en el atributo fields determinan qué campos del modelo Producto se mostrarán en el formulario.
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['unidades']


# Dentro de la clase RegistroForm, se define una clase interna llamada Meta. Esta clase interna se utiliza para configurar metadatos
# relacionados con el formulario. En este caso, se establece el modelo asociado al formulario como User, lo que sugiere que este
# formulario se utiliza para registrar nuevos usuarios en el sistema.

# Además, se especifican los campos que estarán presentes en el formulario. Estos campos son username, email, password1 y password2.
# Estos campos determinan los datos que se solicitarán al usuario durante el proceso de registro.
class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Esta clase hereda de AuthenticationForm.
# - La clase tiene tres atributos: username, password y next.
# - username es un campo de formulario para el nombre de usuario.
# - password es un campo de formulario para la contraseña, y se utiliza el widget forms.PasswordInput para ocultar el texto ingresado.
# - next es un campo de formulario oculto que se utiliza para almacenar la URL a la que se redirigirá después de enviar el formulario.
#  Se establece inicialmente en "/tienda".
class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput, initial="/tienda")


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['user', 'vip', 'saldo']


class DireccionesForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion_envio', 'direccion_facturacion']


class TarjetasForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['nombre_tarjeta', 'tipo_tarjeta', 'titular_tarjeta', 'caducidad_tarjeta']


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto', 'valoracion']


class ComentarioEditForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
