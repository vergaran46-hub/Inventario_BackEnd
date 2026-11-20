from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, ProtectedError
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import Producto, Categoria, Etiqueta, Movimiento
from .forms import ProductoForm, RegistroForm, PerfilForm, CategoriaForm, EtiquetaForm, MovimientoForm


VENTAS_PARA_COMPRAR = 5


# ---------- Inicio ----------

@login_required
def inicio(request):
    por_acabarse = []
    for p in Producto.objects.order_by('nombre'):
        if p.stock_actual <= p.stock_minimo:
            por_acabarse.append(p)
    ultimos = Movimiento.objects.select_related('producto', 'usuario').order_by('-fecha')[:5]
    return render(request, 'inventario/inicio.html', {'por_acabarse': por_acabarse, 'ultimos': ultimos})


# ---------- Entradas y salidas ----------

@login_required
def movimiento_crear(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            producto = movimiento.producto
            with transaction.atomic():
                if movimiento.tipo == 'ENTRADA':
                    producto.stock_actual += movimiento.cantidad
                else:
                    producto.stock_actual -= movimiento.cantidad
                producto.save()
                movimiento.save()
            messages.success(request, f'Listo: ahora quedan {producto.stock_actual} unidades de {producto.nombre}.')
            return redirect('inicio')
        messages.error(request, 'Revisa los datos del formulario.')
    else:
        form = MovimientoForm()
    return render(request, 'inventario/movimiento_form.html', {'form': form})


# ---------- Listado (pantalla principal) ----------

@login_required
def home(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')


    productos = (
        Producto.objects
        .select_related('categoria', 'usuario')
        .prefetch_related('etiquetas')
        .order_by('nombre')
    )
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=categoria_id)

    paginator = Paginator(productos, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'inventario/home.html', {
        'page_obj': page_obj,
        'categorias': Categoria.objects.order_by('nombre'),
        'q': q,
        'categoria_id': categoria_id,
        'querystring': params.urlencode(),
    })


@login_required
def mis_productos(request):
    productos = (
        Producto.objects
        .filter(usuario=request.user)
        .select_related('categoria')
        .prefetch_related('etiquetas')
        .order_by('nombre')
    )
    return render(request, 'inventario/mis_productos.html', {'productos': productos})


# ---------- CRUD ----------

@login_required
def producto_detalle(request, pk):
    producto = get_object_or_404(
        Producto.objects.select_related('categoria', 'usuario').prefetch_related('etiquetas'),
        pk=pk
    )
    return render(request, 'inventario/producto_detalle.html', {'producto': producto})


@login_required
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.usuario = request.user
            producto.save()
            form.save_m2m()   
            messages.success(request, 'Producto creado correctamente.')
            return redirect('home')
        messages.error(request, 'Revisa los datos del formulario.')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto_form.html', {'form': form, 'titulo': 'Agregar un producto'})


@login_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if producto.usuario != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('producto_detalle', pk=producto.pk)
        messages.error(request, 'Revisa los datos del formulario.')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto_form.html', {'form': form, 'titulo': 'Editar producto'})


@login_required
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if producto.usuario != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(request, 'Producto eliminado.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: el producto tiene movimientos registrados.')
        return redirect('home')
    return render(request, 'inventario/producto_eliminar.html', {'producto': producto})


# ---------- Reporte ----------

@login_required
def reporte(request):
    hoy = timezone.localdate()
    try:
        desde = datetime.strptime(request.GET.get('desde', ''), '%Y-%m-%d').date()
        hasta = datetime.strptime(request.GET.get('hasta', ''), '%Y-%m-%d').date()
    except ValueError:
        desde = hoy - timedelta(days=30)
        hasta = hoy
    orden = request.GET.get('orden', 'menos')
    producto_id = request.GET.get('producto', '')

    inicio = timezone.make_aware(datetime.combine(desde, time.min))
    fin = timezone.make_aware(datetime.combine(hasta, time.max))
    ventas = Movimiento.objects.filter(motivo='VENTA', fecha__gte=inicio, fecha__lte=fin)

    productos = Producto.objects.order_by('nombre')
    if producto_id:
        elegidos = productos.filter(pk=producto_id)
    else:
        elegidos = productos

    filas = []
    for p in elegidos:
        vendidas = 0
        for m in ventas:
            if m.producto_id == p.id:
                vendidas += m.cantidad
        filas.append((vendidas, p.nombre, p.stock_actual))
    if orden == 'mas':
        filas.sort(reverse=True)
    else:
        filas.sort()

    maximo = 1
    for f in filas:
        if f[0] > maximo:
            maximo = f[0]
    tabla = []
    for vendidas, nombre, stock in filas:
        tabla.append((vendidas, nombre, stock, vendidas * 100 // maximo))

    aviso = ''
    if tabla and orden == 'menos' and tabla[0][0] < VENTAS_PARA_COMPRAR:
        aviso = f'«{tabla[0][1]}» vendió muy poco en el período (solo {tabla[0][0]}) y quedan {tabla[0][2]} en bodega. Quizás no conviene volver a comprarla.'
    if tabla and orden == 'mas' and tabla[0][0] >= VENTAS_PARA_COMPRAR:
        aviso = f'«{tabla[0][1]}» es lo que más se vendió (en total {tabla[0][0]}) y quedan {tabla[0][2]} en bodega. Conviene no quedarse sin stock.'

    return render(request, 'inventario/reporte.html', {
        'tabla': tabla, 'aviso': aviso, 'productos': productos,
        'desde': desde, 'hasta': hasta,
        'orden': orden, 'producto_id': producto_id,
    })


# ---------- Grupos y etiquetas ----------

@login_required
def grupos(request):
    form_categoria = CategoriaForm()
    form_etiqueta = EtiquetaForm()

    if request.method == 'POST':
        if 'guardar_categoria' in request.POST:
            form_categoria = CategoriaForm(request.POST)
            if form_categoria.is_valid():
                form_categoria.save()
                messages.success(request, 'Grupo creado correctamente.')
                return redirect('grupos')
            messages.error(request, 'Revisa el nombre del grupo.')
        elif 'guardar_etiqueta' in request.POST:
            form_etiqueta = EtiquetaForm(request.POST)
            if form_etiqueta.is_valid():
                form_etiqueta.save()
                messages.success(request, 'Etiqueta creada correctamente.')
                return redirect('grupos')
            messages.error(request, 'Revisa el nombre de la etiqueta.')

    return render(request, 'inventario/grupos.html', {
        'categorias': Categoria.objects.order_by('nombre'),
        'etiquetas': Etiqueta.objects.order_by('nombre'),
        'form_categoria': form_categoria,
        'form_etiqueta': form_etiqueta,
    })


# ---------- Cuenta de usuario ----------

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
            return redirect('login')
        messages.error(request, 'Revisa los datos del formulario.')
    else:
        form = RegistroForm()
    return render(request, 'inventario/registro.html', {'form': form})


@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tus datos fueron actualizados.')
            return redirect('perfil')
        messages.error(request, 'Revisa los datos del formulario.')
    else:
        form = PerfilForm(instance=request.user)
    total = request.user.productos.count()
    return render(request, 'inventario/perfil.html', {'form': form, 'total': total})


class CambiarPasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'inventario/cambiar_password.html'
    success_url = reverse_lazy('perfil')
    success_message = 'Tu contraseña fue actualizada.'