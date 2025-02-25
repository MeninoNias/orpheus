from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.admin import default_site
from .models import Artist, Playlist, PlaylistTrack, Track


@admin.register(Artist, site=default_site)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['artist_name_with_photo', 'platform',
                    'tracks_count', 'owner', 'created_at']
    list_filter = ['platform', 'created_at', 'owner']
    search_fields = ['name', 'bio', 'platform__name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'platform', 'profile_picture')
        }),
        (_('Biografia'), {
            'fields': ('bio',),
            'classes': ('collapse',)
        }),
        (_('Informações do Sistema'), {
            'fields': ('owner', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def artist_name_with_photo(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; margin-right: 10px">{}', obj.profile_picture, obj.name
            )
        return obj.name
    artist_name_with_photo.short_description = _('Artista')

    def tracks_count(self, obj):
        return obj.tracks.count()
    tracks_count.short_description = _('Faixas')


class PlaylistTrackInline(admin.TabularInline):
    model = PlaylistTrack
    extra = 1
    ordering = ['position']
    raw_id_fields = ['track']


@admin.register(Track, site=default_site)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'platform',
                    'duration_formatted', 'source_type_badge', 'playlists_count']
    list_filter = ['source_type', 'platform', 'created_at', 'artist']
    search_fields = ['title', 'artist__name', 'url']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['artist']

    fieldsets = (
        (_('Informações Básicas'), {
            'fields': (('title', 'artist'), 'platform', 'url', 'duration')
        }),
        (_('Arquivos'), {
            'fields': ('source_type', 'audio_file', 'file'),
            'classes': ('collapse',)
        }),
        (_('Informações do Sistema'), {
            'fields': ('owner', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def duration_formatted(self, obj):
        minutes = obj.duration // 60
        seconds = obj.duration % 60
        return f'{minutes}:{seconds:02d}'
    duration_formatted.short_description = _('Duração')

    def source_type_badge(self, obj):
        colors = {'URL': 'green', 'FILE': 'blue'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px">{}</span>',
            colors[obj.source_type], obj.get_source_type_display()
        )
    source_type_badge.short_description = _('Origem')

    def playlists_count(self, obj):
        return obj.playlists.count()
    playlists_count.short_description = _('Playlists')


@admin.register(Playlist, site=default_site)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'tracks_count',
                    'total_duration', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description', 'user__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PlaylistTrackInline]

    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'user', 'description')
        }),
        (_('Informações do Sistema'), {
            'fields': ('owner', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tracks_count(self, obj):
        return obj.tracks.count()
    tracks_count.short_description = _('Faixas')

    def total_duration(self, obj):
        total_seconds = sum(track.duration for track in obj.tracks.all())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f'{hours}:{minutes:02d}:{seconds:02d}'
        return f'{minutes}:{seconds:02d}'
    total_duration.short_description = _('Duração Total')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tracks')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(PlaylistTrack, site=default_site)
class PlayListTrackAdmin(admin.ModelAdmin):
    list_display = ['track', 'position', 'playlist']
    list_filter = ['playlist']
    search_fields = ['track__title', 'playlist__name']
    raw_id_fields = ['track', 'playlist']
    readonly_fields = ['created_at', 'updated_at']
    