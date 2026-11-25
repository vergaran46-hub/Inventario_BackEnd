# Inventario_BackEnd

Sistema de inventario para RG Beauty Spa, hecho con Django y MySQL.

Proyecto Integrado, equipo 6 (INACAP Sede Copiapó).

## Qué hace

- Registra productos con su grupo y etiquetas.
- Registra entradas y salidas de productos y actualiza el stock.
- Avisa en la pantalla de inicio cuando un producto se está acabando.
- Permite buscar productos por nombre y filtrarlos por grupo.
- Muestra un reporte de ventas por periodo, con los productos más y menos vendidos.
- Cada persona tiene su cuenta para ingresar al sistema.

## Cómo instalarlo

1. Instalar Python y MySQL.
2. Instalar las librerías del proyecto: `pip install -r requirements.txt`
3. Crear en MySQL una base de datos llamada `inventario_BackEnd`.
4. Crear las tablas: `python manage.py migrate`
5. Crear un usuario administrador: `python manage.py createsuperuser`
6. Encender el sistema: `python manage.py runserver`
7. Abrir en el navegador: http://127.0.0.1:8000/

Los datos de conexión a MySQL están en `config/settings.py`, en la parte DATABASES.

## Equipo 6

- Ignacio Vergara Soto
- Herbert Urtubia Vega
- Abraham Arancibia Arancibia
- Javier Contreras Gallardos


## -----------------------------------------------------------------------------------------------

## Casos de prueba manuales

Se prueban a mano en el navegador. La columna Resultado se completa con OK o Falló.

| N° | Qué se prueba | Qué debe pasar | Resultado |
|----|---------------|----------------|-----------|
| 1 | Registrarse con un correo que ya existe | Muestra "Ese correo ya está registrado." | |
| 2 | Registrarse con la contraseña 12345678 | Muestra un error de contraseña y no crea la cuenta | |
| 3 | Ingresar con usuario y contraseña correctos | Entra a Productos en bodega | |
| 4 | Ingresar con la contraseña incorrecta | Muestra un error y no deja entrar | |
| 5 | Abrir /productos/ sin haber iniciado sesión | Lleva a la pantalla de ingreso | |
| 6 | Agregar un producto con el nombre "ab" | Muestra "El nombre debe tener al menos 3 caracteres." | |
| 7 | Agregar un producto con 0 unidades | No deja guardar y avisa que debe haber al menos 1 | |
| 8 | Agregar un producto con 101 unidades | Muestra "El máximo es 100 unidades." | |
| 9 | Agregar un producto con datos correctos | Muestra "Producto creado correctamente." y aparece en la lista | |
| 10 | Registrar una entrada de 5 unidades | El stock sube 5 y muestra el mensaje "Listo: ahora quedan..." | |
| 11 | Registrar una salida de 2 unidades | El stock baja 2 | |
| 12 | Registrar una salida de más unidades de las que hay | Muestra "Hay X unidades y se piden Y." y no cambia el stock | |
| 13 | Dejar un producto con stock igual o menor al mínimo | Aparece en "Se están acabando" en Inicio | |
| 14 | Buscar un producto por parte del nombre | Solo muestra los productos que coinciden | |
| 15 | Filtrar la lista por un grupo | Solo muestra los productos de ese grupo | |
| 16 | Editar un producto creado por otro usuario | Muestra la página de acceso denegado (403) | |
| 17 | Eliminar un producto sin movimientos | Muestra "Producto eliminado." | |
| 18 | Eliminar un producto que tiene movimientos | Muestra "No se puede eliminar: el producto tiene movimientos registrados." | |
| 19 | Crear un grupo que ya existe | Muestra "Ese grupo ya existe." | |
| 20 | Cerrar sesión | Vuelve a la pantalla de ingreso | |
| 21 | Registrarse con la contraseña Abc12345 (8 caracteres) | Rechaza la contraseña por ser demasiado corta | |
| 22 | Mirar Inicio después de registrar más de 5 movimientos | La tabla "Últimos movimientos" muestra solo 5, el más nuevo arriba | |
| 23 | Registrar una entrada con motivo Venta | Muestra "Una entrada solo puede ser por compra." y no cambia el stock | |
| 24 | Registrar una salida con motivo Compra | Muestra "Una salida solo puede ser por venta o uso interno." y no cambia el stock | |
| 25 | Abrir Reportes en el menú | Muestra el Reporte de ventas con el periodo de los últimos 30 días y la tabla con puesto, producto, unidades vendidas, barra y cuántas quedan | |
| 26 | Elegir "Los más vendidos" y presionar Ver reporte | La tabla se ordena del producto que más se vendió al que menos | |
| 27 | Elegir un producto en "Producto (opcional)" y presionar Ver reporte | Solo aparece ese producto en la tabla | |
| 28 | Elegir un periodo que no incluye las ventas registradas | Las unidades vendidas aparecen en 0 | |
| 29 | Mirar un producto que vendió menos de 5 unidades, ordenado por "Los menos vendidos" | Aparece el recuadro "Para pensar" con la sugerencia de no volver a comprarlo | |