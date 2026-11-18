import logging

from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

auditoria = logging.getLogger('inventario.auditoria')


# ---------- Cambios de roles ----------

@receiver(m2m_changed, sender=User.groups.through)
def registrar_cambio_de_grupos(sender, instance, action, pk_set, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        auditoria.warning('cambio de grupos instancia=%s accion=%s grupos=%s', instance.pk, action, sorted(pk_set or []))