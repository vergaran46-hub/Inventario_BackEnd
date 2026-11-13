from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
 
from .models import Categoria, Producto
 
 
class BaseSeguridad(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_user('romina', 'romina@example.com', 'ClaveSegura#2026')
        self.admin.groups.add(Group.objects.get(name='Administradora'))
        self.asistente = User.objects.create_user('asis', 'asis@example.com', 'ClaveSegura#2026')
        self.asistente.groups.add(Group.objects.get(name='Asistente'))
        self.categoria = Categoria.objects.create(nombre='Facial')
        self.producto = Producto.objects.create(
            nombre='Crema hidratante', categoria=self.categoria,
            stock_actual=10, stock_minimo=3, usuario=self.admin,
        )
 
    def entrar(self, usuario):
        self.client.login(username=usuario, password='ClaveSegura#2026')
 
 
class RolesTests(BaseSeguridad):
    def test_roles_existen(self):
        self.assertTrue(Group.objects.filter(name='Administradora').exists())
        self.assertTrue(Group.objects.filter(name='Asistente').exists())
 
    def test_rutas_protegidas_redirigen_al_login(self):
        for nombre, args in [('inicio', []), ('home', []), ('movimiento_crear', []),
                             ('producto_crear', []), ('producto_editar', [self.producto.pk]),
                             ('producto_eliminar', [self.producto.pk]), ('grupos', []), ('perfil', [])]:
            r = self.client.get(reverse(nombre, args=args))
            self.assertEqual(r.status_code, 302, nombre)
            self.assertIn(reverse('login'), r.url, nombre)
 
    def test_asistente_no_puede_crear_editar_ni_eliminar(self):
        self.entrar('asis')
        for nombre, args in [('producto_crear', []), ('producto_editar', [self.producto.pk]),
                             ('producto_eliminar', [self.producto.pk]), ('grupos', [])]:
            r = self.client.get(reverse(nombre, args=args))
            self.assertEqual(r.status_code, 403, nombre)
 
    def test_asistente_puede_ver_productos_y_registrar_movimientos(self):
        self.entrar('asis')
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        r = self.client.post(reverse('movimiento_crear'), {
            'producto': self.producto.pk, 'tipo': 'SALIDA', 'motivo': 'VENTA', 'cantidad': 2})
        self.assertEqual(r.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 8)
 
    def test_administradora_puede_crear_editar_y_eliminar(self):
        self.entrar('romina')
        r = self.client.post(reverse('producto_editar', args=[self.producto.pk]), {
            'nombre': 'Crema facial', 'categoria': self.categoria.pk,
            'descripcion': '', 'stock_actual': 10, 'stock_minimo': 3})
        self.assertEqual(r.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Crema facial')
        r = self.client.post(reverse('producto_eliminar', args=[self.producto.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())
 
    def test_asistente_no_ve_botones_de_edicion(self):
        self.entrar('asis')
        r = self.client.get(reverse('home'))
        self.assertNotContains(r, 'Editar')
        self.assertNotContains(r, 'Agregar un producto')
 
 
class RegistroTests(BaseSeguridad):
    def test_registro_cerrado_responde_404(self):
        self.assertEqual(self.client.get(reverse('registro')).status_code, 404)
 
    @override_settings(REGISTRO_ABIERTO=True)
    def test_registro_abierto_responde_200(self):
        self.assertEqual(self.client.get(reverse('registro')).status_code, 200)
 
 
class LoginTests(BaseSeguridad):
    def test_bloqueo_tras_cinco_intentos_fallidos(self):
        for _ in range(5):
            self.client.post(reverse('login'), {'username': 'romina', 'password': 'mala'})
        r = self.client.post(reverse('login'), {'username': 'romina', 'password': 'ClaveSegura#2026'})
        self.assertEqual(r.status_code, 429)
 
    def test_login_correcto_reinicia_los_intentos(self):
        for _ in range(3):
            self.client.post(reverse('login'), {'username': 'romina', 'password': 'mala'})
        r = self.client.post(reverse('login'), {'username': 'romina', 'password': 'ClaveSegura#2026'})
        self.assertEqual(r.status_code, 302)
 
    def test_contrasena_se_guarda_cifrada(self):
        self.assertTrue(self.admin.password.startswith('pbkdf2_'))
        self.assertNotIn('ClaveSegura', self.admin.password)
 
 
class ProteccionesTests(BaseSeguridad):
    def test_post_sin_token_csrf_es_rechazado(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.login(username='romina', password='ClaveSegura#2026')
        r = cliente.post(reverse('movimiento_crear'), {
            'producto': self.producto.pk, 'tipo': 'SALIDA', 'motivo': 'VENTA', 'cantidad': 1})
        self.assertEqual(r.status_code, 403)
 
    def test_busqueda_con_comillas_no_rompe(self):
        self.entrar('romina')
        r = self.client.get(reverse('home'), {'q': "' OR 1=1 --"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['page_obj']), 0)
 
    def test_entrada_html_se_escapa_en_pantalla(self):
        self.entrar('romina')
        Producto.objects.create(nombre='<script>alert(1)</script>', stock_actual=1, stock_minimo=1, usuario=self.admin)
        r = self.client.get(reverse('home'))
        self.assertNotContains(r, '<script>alert(1)</script>')
