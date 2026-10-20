from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'stock_actual', 'stock_minimo']
        labels = {
            'nombre': 'Nombre del producto',
            'categoria': '¿A que grupo pertenece?',
            'descripcion': 'Descripcion (opcional)',
            'stock_actual': '¿Cuantas unidades tienes hoy?',
            'stock_minimo': 'Avisarme cuando queden...',
        } 
        help_texts = {
            'stock_minimo': 'Cuando queden estas unidades o menos el sistema te avisara que hay que comprar.',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Por Ejemplo: Crema hidratante facial'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Por ejemplo: pote de 250 ml'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = 'sin grupo'