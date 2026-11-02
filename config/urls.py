from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from inventario import views

"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('mis-productos/', views.mis_productos, name='mis_productos'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('producto/nuevo/', views.producto_crear, name='producto_crear'),
    path('producto/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('producto/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('registro/', views.registro, name='registro'),
    path('cuenta/', views.perfil, name='perfil'),
    path('cuenta/password/', views.CambiarPasswordView.as_view(), name='cambiar_password'),
    path('login/', auth_views.LoginView.as_view(template_name='inventario/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]