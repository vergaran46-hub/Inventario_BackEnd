from django.conf import settings

from .permisos import es_administradora


def opciones(request):
    return {
        'es_administradora': es_administradora(request.user),
        'registro_abierto': settings.REGISTRO_ABIERTO,
    }