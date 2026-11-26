import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Producto, Categoria, Etiqueta, Movimiento
 
 
LIMITE_STOCK = 100
MINIMO_AL_CREAR = 1
 
 
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'etiquetas', 'descripcion', 'stock_actual', 'stock_minimo', 'fecha_compra']
        labels = {
            'nombre': 'Nombre del producto',
            'categoria': '¿A qué grupo pertenece?',
            'etiquetas': 'Etiquetas (opcional)',
            'descripcion': 'Descripción (opcional)',
            'stock_actual': '¿Cuántas unidades tienes hoy?',
            'stock_minimo': 'Avisarme cuando queden...',
            'fecha_compra': '¿Cuándo se compró? (opcional)',
        }
        help_texts = {
            'etiquetas': 'Marca todas las que apliquen.',
            'stock_minimo': 'Cuando queden estas unidades o menos, el sistema te avisará que hay que comprar.',
            'fecha_compra': 'Es la fecha de la factura. La fecha de registro la pone el sistema con la fecha de hoy.',
        }
        error_messages = {
            'nombre': {'required': 'Falta el nombre del producto. Escríbelo para poder guardar.'},
            'stock_actual': {'required': 'Escribe cuántas unidades hay hoy (puede ser 0).'},
            'stock_minimo': {'required': 'Escribe en cuántas unidades quieres el aviso.'},
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Por ejemplo: Crema hidratante facial'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Por ejemplo: pote de 250 ml'}),
            'etiquetas': forms.CheckboxSelectMultiple,
            'stock_actual': forms.NumberInput(attrs={'min': 0, 'max': LIMITE_STOCK}),
            'stock_minimo': forms.NumberInput(attrs={'min': 0, 'max': LIMITE_STOCK}),
            'fecha_compra': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.order_by('nombre')
        self.fields['categoria'].empty_label = 'Sin grupo'
        self.fields['etiquetas'].queryset = Etiqueta.objects.order_by('nombre')
        if self.instance.pk is None:
            self.fields['stock_actual'].widget.attrs['min'] = MINIMO_AL_CREAR
 
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if nombre.isdigit():
            raise forms.ValidationError('El nombre debe incluir letras, no solo números.')
        return nombre
 
    def clean_stock_actual(self):
        cantidad = self.cleaned_data['stock_actual']
 
        if cantidad < MINIMO_AL_CREAR and self.instance.pk is None:
            raise forms.ValidationError(f'Para agregar un producto debe haber al menos {MINIMO_AL_CREAR} unidades.')
        if cantidad > LIMITE_STOCK:
            raise forms.ValidationError(f'El máximo es {LIMITE_STOCK} unidades.')
        return cantidad
 
    def clean_fecha_compra(self):
        fecha = self.cleaned_data['fecha_compra']
        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError('La fecha de compra no puede ser futura.')
        return fecha
 
    def clean_stock_minimo(self):
        minimo = self.cleaned_data['stock_minimo']
        if minimo > LIMITE_STOCK:
            raise forms.ValidationError(f'El máximo es {LIMITE_STOCK} unidades.')
        return minimo
 
 
class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
 
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
 
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ese correo ya está registrado.')
        return email
 
 
class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
 
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ese correo ya lo usa otra persona.')
        return email
 
 
class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'tipo', 'motivo', 'cantidad']
        labels = {
            'producto': '¿Qué producto es?',
            'tipo': '¿Qué pasó con el producto?',
            'motivo': '¿Por qué?',
            'cantidad': '¿Cuántas unidades?',
        }
        widgets = {'tipo': forms.RadioSelect}
 
    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise forms.ValidationError('Escribe una cantidad mayor que cero.')
        if cantidad > LIMITE_STOCK:
            raise forms.ValidationError(f'El máximo es {LIMITE_STOCK} unidades.')
        return cantidad
 
    def clean(self):
        datos = super().clean()
        producto = datos.get('producto')
        tipo = datos.get('tipo')
        motivo = datos.get('motivo')
        cantidad = datos.get('cantidad')
        if tipo == 'ENTRADA' and motivo in ('VENTA', 'USO_INTERNO'):
            self.add_error('motivo', 'Una entrada solo puede ser por compra.')
        if tipo == 'SALIDA' and motivo == 'COMPRA':
            self.add_error('motivo', 'Una salida solo puede ser por venta o uso interno.')
        if tipo == 'SALIDA' and producto and cantidad and cantidad > producto.stock_actual:
            self.add_error('cantidad', f'Hay {producto.stock_actual} unidades y se piden {cantidad}.')
        return datos
 
 
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        labels = {'nombre': 'Nombre del grupo'}
        widgets = {'nombre': forms.TextInput(attrs={'placeholder': 'Por ejemplo: Facial'})}
        error_messages = {'nombre': {'required': 'Escribe el nombre del grupo.'}}
 
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ese grupo ya existe.')
        return nombre
 
 
class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nombre']
        labels = {'nombre': 'Nombre de la etiqueta'}
        widgets = {'nombre': forms.TextInput(attrs={'placeholder': 'Por ejemplo: Frágil'})}
        error_messages = {'nombre': {'required': 'Escribe el nombre de la etiqueta.'}}
 
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if Etiqueta.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Esa etiqueta ya existe.')
        return nombre
