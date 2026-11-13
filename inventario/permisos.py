from functools import wraps

from django.core.exceptions import PermissionDenied


# ---------- Roles ----------

def es_administradora(usuario):
    if not usuario.is_authenticated:
        return False
    return usuario.is_superuser or usuario.groups.filter(name='Administradora').exists()


def solo_administradora(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not es_administradora(request.user):
            raise PermissionDenied
        return vista(request, *args, **kwargs)
    return envoltura