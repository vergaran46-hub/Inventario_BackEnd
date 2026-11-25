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