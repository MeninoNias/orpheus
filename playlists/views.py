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
        
        # Passar o request para os forms do inline
        for formset in inlines:
            formset.request = self.request
            for inline_form in formset.forms:
                inline_form.request = self.request
        
        response = super().forms_valid(form, inlines)

        for formset in inlines:
            for index, inline_form in enumerate(formset.forms):
                if inline_form.is_valid() and not inline_form.cleaned_data.get('DELETE', False):
                    instance = inline_form.save(commit=False)
                    instance.position = index
                    instance.playlist = form.instance
                    instance.owner = self.request.user
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
        form.instance.user = self.request.user
        form.instance.owner = self.request.user
        
        try:
            # Primeiro, salva o formulário principal
            self.object = form.save()
            
            # Depois, processa os inlines
            for formset in inlines:
                # Deleta todos os tracks existentes para recriar com novas posições
                self.object.playlist_tracks.all().delete()
                
                # Filtra apenas os formulários válidos e não marcados para deleção
                valid_forms = [
                    f for f in formset.forms 
                    if f.is_valid() and not f.cleaned_data.get('DELETE')
                ]
                
                # Salva cada track com sua nova posição
                for index, inline_form in enumerate(valid_forms):
                    try:
                        print(f"Salvando track {index}: {inline_form.cleaned_data}")
                        instance = inline_form.save(commit=False)
                        instance.position = index + 1
                        instance.playlist = self.object
                        instance.owner = self.request.user
                        instance.save()
                        print(f"Salvou track {index}: {instance}")
                    except Exception as e:
                        print(f"Erro ao salvar track {index}: {e}")

            return super().forms_valid(form, inlines)
            
        except Exception as e:
            print(f"Erro no forms_valid: {e}")
            raise


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
