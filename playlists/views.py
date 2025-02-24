from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, View
from extra_views import (CreateWithInlinesView, InlineFormSetFactory,
                         UpdateWithInlinesView)

from downloader.services.youtube import YouTubeService

from .forms import PlaylistForm, PlaylistTrackInline
from .models import Playlist


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
            # Ordenação do mais recente para o mais antigo
        ).order_by('-created_at')


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
    form_class = PlaylistForm
    inlines = [PlaylistTrackInline]
    template_name = 'playlists/playlist_form.html'
    success_url = reverse_lazy('playlists:list')

    def forms_valid(self, form, inlines):
        form.instance.user = self.request.user
        form.instance.owner = self.request.user
        
        print("Form Data:", form.cleaned_data)
        print("Inlines Data:", [inline.cleaned_data for inline in inlines[0]])
        
        response = super().forms_valid(form, inlines)

        for index, formset in enumerate(inlines):
            for inline_form in formset:
                if inline_form.cleaned_data and not inline_form.cleaned_data.get('DELETE', False):
                    instance = inline_form.instance
                    instance.position = index
                    instance.save()

        return response


class PlaylistUpdateView(LoginRequiredMixin, UpdateWithInlinesView):
    model = Playlist
    form_class = PlaylistForm
    inlines = [PlaylistTrackInline]
    template_name = 'playlists/playlist_form.html'
    success_url = reverse_lazy('playlists:list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def forms_valid(self, form, inlines):
        print(self.request.POST)
        response = super().forms_valid(form, inlines)
        
        print("Form Data:", form.cleaned_data)
        print("Inlines Data:", [
            [f.cleaned_data for f in formset.forms] 
            for formset in inlines
        ])
        
        for formset in inlines:
            for index, inline_form in enumerate(formset.forms):
                if inline_form.is_valid() and not inline_form.cleaned_data.get('DELETE'):
                    instance = inline_form.save(commit=False)
                    instance.position = index
                    instance.playlist = form.instance
                    instance.save()

        return response


class SearchTrackView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse({'tracks': []})

        try:
            youtube_service = YouTubeService()
            youtube_service.user = request.user
            tracks = youtube_service.search_faixa(query)
            
            return JsonResponse({
                'tracks': [{
                    'url': track.get('url'),
                    'title': track.get('title'),
                    'duration': track.get('duration'),
                    'thumbnail': track.get('thumbnail')
                } for track in tracks]
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
