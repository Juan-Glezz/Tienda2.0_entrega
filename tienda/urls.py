from django.urls import path
from . import views
from .views import WelcomeView,ProductosView,CompraView,Post_EditView,Post_eliminarView,Post_Nuevo_View,Log_In_View,TopProducto_Views,Log_outView
urlpatterns = [
    path('', CompraView.as_view(), name='welcome'),
    path('tienda/', CompraView.as_view(), name='compra'),
    path('tienda/admin/productos', ProductosView.as_view(), name='productos'),
    path('tienda/admin/editar/<int:pk>', Post_EditView.as_view(), name='editar'),
    path('tienda/admin/eliminar/<int:pk>', Post_eliminarView.as_view(), name='eliminar'),
    path('tienda/admin/nuevo/', Post_Nuevo_View.as_view(), name='nuevo'),
    path('tienda/mostrarBusqueda/', views.post_buscar, name='buscar'),
    path('tienda/login/', Log_In_View.as_view(), name='login'),
    path('tienda/checkout/<int:pk>/', views.checkout, name='checkout'),
    path('tienda/logout/', Log_outView.as_view(), name='logout'),
    path('tienda/informes/top10Compras/',TopProducto_Views.as_view(), name='top_productos'),
    path('tienda/informes/top10mejores/', views.topClientes, name='top_clientes'),
    path('tienda/informes/historialCompras/', views.historial, name='historial'),
]