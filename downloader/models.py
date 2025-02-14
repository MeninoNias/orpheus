from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseUUidModel


class Platform(BaseUUidModel):
    """
    Modelo para armazenar informações sobre plataformas de streaming.
    Ex: YouTube, SoundCloud, etc.
    """
    name = models.CharField(
        _('Nome'),
        max_length=50,
        unique=True,
        help_text=_('Nome da plataforma (ex: YouTube, SoundCloud)')
    )
    base_url = models.URLField(
        _('URL Base'),
        blank=True,
        help_text=_('URL base da plataforma (ex: https://youtube.com)')
    )
    logo = models.URLField(
        _('Logo'),
        blank=True,
        help_text=_('URL do logo da plataforma')
    )
    active = models.BooleanField(
        _('Ativo'),
        default=True,
        help_text=_('Indica se a plataforma está ativa para uso')
    )

    class Meta:
        verbose_name = _('Plataforma')
        verbose_name_plural = _('Plataformas')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Retorna a URL base da plataforma."""
        return self.base_url