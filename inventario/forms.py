from django import forms
from django.contrib.auth.models import User
from .models import Producto, Movimiento


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'stock_actual', 'stock_minimo']
        labels = {
            'nombre': 'Nombre del producto',
            'categoria': '¿A qué grupo pertenece?',
            'descripcion': 'Descripción (opcional)',
            'stock_actual': '¿Cuántas unidades tienes hoy?',
            'stock_minimo': 'Avisarme cuando queden...',
        }
        help_texts = {
            'stock_minimo': 'Cuando queden estas unidades o menos, el sistema te avisará que hay que comprar.',
        }
        error_messages = {
            'nombre': {'required': 'Falta el nombre del producto. Escríbelo para poder guardar.'},
            'stock_actual': {'required': 'Escribe cuántas unidades hay hoy (puede ser 0).'},
            'stock_minimo': {'required': 'Escribe en cuántas unidades quieres el aviso.'},
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Por ejemplo: Crema hidratante facial'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Por ejemplo: pote de 250 ml'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = 'Sin grupo'


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
        widgets = {
            'tipo': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.fields['tipo'].choices = [
            ('ENTRADA', 'Llegó mercadería'),
            ('SALIDA', 'Se vendió o se usó'),
        ]

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise forms.ValidationError('Escribe una cantidad mayor que cero.')
        return cantidad

    def clean(self):
        datos = super().clean()
        producto = datos.get('producto')
        tipo = datos.get('tipo')
        motivo = datos.get('motivo')
        cantidad = datos.get('cantidad')


        if tipo == 'ENTRADA' and motivo and motivo != 'COMPRA':
            self.add_error('motivo', 'Si llegó mercadería, el motivo es Compra.')
        if tipo == 'SALIDA' and motivo and motivo == 'COMPRA':
            self.add_error('motivo', 'Si el producto salió, elige Venta o Uso interno.')

    
        if tipo == 'SALIDA' and producto and cantidad:
            if cantidad > producto.stock_actual:
                self.add_error(
                    'cantidad',
                    f'Hay {producto.stock_actual} unidades y se piden {cantidad}. Escribe {producto.stock_actual} o menos.'
                )
        return datos


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }