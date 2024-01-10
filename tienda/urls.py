from django.urls import path
from . import views

urlpatterns = [
    path('', views.compra, name='welcome'),
    path('tienda/', views.compra, name='compra'),
    path('tienda/admin/productos', views.productos, name='productos'),
    path('tienda/admin/editar/<int:pk>', views.post_edit, name='editar'),
    path('tienda/admin/eliminar/<int:pk>', views.post_eliminar, name='eliminar'),
    path('tienda/admin/nuevo/', views.post_nuevo, name='nuevo'),
    path('tienda/mostrarBusqueda/', views.post_buscar, name='buscar'),
    path('tienda/login/', views.log_in, name='login'),
    path('tienda/checkout/<int:pk>/', views.checkout, name='checkout'),
    path('tienda/logout/', views.log_out, name='logout'),
    path('tienda/informes/top10Compras/', views.topProductos, name='top_productos'),
    path('tienda/informes/top10mejores/', views.topClientes, name='top_clientes'),
    path('tienda/informes/historialCompras/', views.historial, name='historial'),
]