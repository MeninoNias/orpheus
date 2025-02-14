from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseOwnerModel
from downloader.models import Platform
from users.models import User


class Artist(BaseOwnerModel):
    """Modelo para armazenar informações dos artistas."""
    
    name = models.CharField(_('Nome'), max_length=255)
    platform = models.ForeignKey(
        Platform, 
        on_delete=models.CASCADE,
        verbose_name=_('Plataforma')
    )
    bio = models.TextField(_('Biografia'), blank=True)
    profile_picture = models.URLField(_('Foto do Perfil'), blank=True)

    class Meta:
        verbose_name = _('Artista')
        verbose_name_plural = _('Artistas')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.platform.name})"


class Track(BaseOwnerModel):
    """Modelo para armazenar informações de faixas de áudio."""
    
    SOURCE_CHOICES = [
        ('URL', _('Online')),
        ('FILE', _('Local'))
    ]

    # Informações básicas
    title = models.CharField(_('Título'), max_length=255)
    artist = models.ForeignKey(
        Artist, 
        on_delete=models.CASCADE, 
        related_name='tracks',
        verbose_name=_('Artista')
    )
    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        verbose_name=_('Plataforma')
    )
    url = models.URLField(_('URL'))
    duration = models.IntegerField(
        _('Duração em segundos'),
        help_text=_('Duração da faixa em segundos')
    )

    # Arquivos
    audio_file = models.FileField(
        _('Arquivo de áudio'),
        upload_to='tracks/',
        help_text=_('Arquivo de áudio processado')
    )
    source_type = models.CharField(
        _('Tipo de origem'),
        max_length=10,
        choices=SOURCE_CHOICES,
        default='URL'
    )
    file = models.FileField(
        _('Arquivo local'),
        upload_to='uploads/',
        blank=True,
        help_text=_('Arquivo local para upload direto')
    )

    class Meta:
        verbose_name = _('Faixa')
        verbose_name_plural = _('Faixas')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'artist']),
            models.Index(fields=['platform', 'url'])
        ]

    def __str__(self):
        return f"{self.title} - {self.artist.name} ({self.get_source_type_display()})"


class Playlist(BaseOwnerModel):
    """Modelo para armazenar playlists dos usuários."""

    name = models.CharField(_('Nome'), max_length=255)
    description = models.TextField(_('Descrição'), blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Usuário'),
        related_name='playlists'
    )
    tracks = models.ManyToManyField(
        Track,
        through='PlaylistTrack',
        verbose_name=_('Faixas'),
        related_name='playlists'
    )

    class Meta:
        verbose_name = _('Playlist')
        verbose_name_plural = _('Playlists')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'user'])
        ]

    def __str__(self):
        return f"{self.name} ({self.user.name})"


class PlaylistTrack(BaseOwnerModel):
    """Modelo intermediário para ordenar faixas em playlists."""

    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        verbose_name=_('Faixa'),
        related_name='playlist_tracks'
    )
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        verbose_name=_('Playlist'),
        related_name='playlist_tracks'
    )
    position = models.PositiveIntegerField(
        _('Posição'),
        default=0,
        help_text=_('Ordem da faixa na playlist')
    )

    class Meta:
        verbose_name = _('Faixa da Playlist')
        verbose_name_plural = _('Faixas da Playlist')
        ordering = ['playlist', 'position']
        unique_together = ['playlist', 'position']
        indexes = [
            models.Index(fields=['playlist', 'position'])
        ]

    def __str__(self):
        return f"{self.playlist.name} - {self.track.title} ({self.position})"

    def save(self, *args, **kwargs):
        """Ajusta automaticamente a posição ao salvar."""
        if not self.position:
            last_position = PlaylistTrack.objects.filter(
                playlist=self.playlist
            ).aggregate(models.Max('position'))['position__max']
            self.position = (last_position or 0) + 1
        super().save(*args, **kwargs)
