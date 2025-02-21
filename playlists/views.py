from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from extra_views import (
    CreateWithInlinesView, UpdateWithInlinesView, 
    InlineFormSetFactory
)

from .models import Playlist, PlaylistTrack, Track
from downloader.services.youtube import YouTubeService


class PlaylistTrackInline(InlineFormSetFactory):
    model = PlaylistTrack
    fields = ['track', 'position']
    factory_kwargs = {
        'extra': 1,
        'can_delete': True,
        'can_order': True,
    }


class PlaylistListView(LoginRequiredMixin, ListView):
    model = Playlist
    template_name = 'playlists/playlist_list.html'
    context_object_name = 'playlists'

    def get_queryset(self):
        return Playlist.objects.filter(
            user=self.request.user
        ).select_related(
            'user'
        ).prefetch_related(
            'tracks'
        ).order_by('-created_at')  # Ordenação do mais recente para o mais antigo


class PlaylistDetailView(LoginRequiredMixin, DetailView):
    model = Playlist
    template_name = 'playlists/playlist_detail.html'
    context_object_name = 'playlist'

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        ).prefetch_related('tracks')


class PlaylistCreateView(LoginRequiredMixin, CreateWithInlinesView):
    model = Playlist
    inlines = [PlaylistTrackInline]
    fields = ['name', 'description']
    template_name = 'playlists/playlist_form.html'
    success_url = reverse_lazy('playlists:list')

    def forms_valid(self, form, inlines):
        form.instance.user = self.request.user
        form.instance.owner = self.request.user
        return super().forms_valid(form, inlines)


class PlaylistUpdateView(LoginRequiredMixin, UpdateWithInlinesView):
    model = Playlist
    inlines = [PlaylistTrackInline]
    fields = ['name', 'description']
    template_name = 'playlists/playlist_form.html'
    success_url = reverse_lazy('playlists:list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    
class SearchTrackView(LoginRequiredMixin, View):
    
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse({'tracks': []})
        
        youtube_service = YouTubeService()
        youtube_service.user = request.user
        tracks = youtube_service.search_faixa(query)
        
        return JsonResponse({'tracks': tracks})