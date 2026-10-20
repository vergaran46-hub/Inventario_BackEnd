from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Producto

# Create your views here.

@login_required
def home(request):
    productos = Producto.objects.all()
    productos_bajos = []
    for p in productos:
        if p.stock_actual <= p.stock_minimo:
            productos_bajos.append(p)

    return render(request, 'inventario/home.html', {
        'total_productos': productos.count(),
        'productos_bajos': productos_bajos,
    })