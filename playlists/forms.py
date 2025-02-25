from django import forms
from django.utils.translation import gettext_lazy as _
from extra_views import InlineFormSetFactory

from downloader.services.youtube import YouTubeService
from playlists.models import Playlist, PlaylistTrack, Track


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PlaylistTrackForm(forms.ModelForm):
    track_url = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
        error_messages={
            'required': _('A URL da faixa é obrigatória')
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se já existe uma track, preenche o track_url
        if self.instance and hasattr(self.instance, "track"):
            self.initial['track_url'] = self.instance.track.url

    class Meta:
        model = PlaylistTrack
        fields = ['track_url', 'position']
        widgets = {
            'position': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        print("Limpando dados:", cleaned_data)
        track_url = cleaned_data.get('track_url')

        if not track_url and not self.cleaned_data.get('DELETE', False):
            raise forms.ValidationError(_('URL da faixa é obrigatória'))

        if self.cleaned_data.get('DELETE', False):
            return cleaned_data

        try:
            youtube_service = YouTubeService()
            if hasattr(self, 'request'):
                youtube_service.user = self.request.user
            else:
                youtube_service.user = self.instance.playlist.user if self.instance.playlist else None

            print(f"Buscando informações da track: {track_url}")
            track_info = youtube_service.get_track_info(track_url)

            if track_info:
                track, created = Track.objects.get_or_create(
                    url=track_info['url'],
                    defaults={
                        'artist': track_info['artist'],
                        'platform': track_info['platform'],
                        'title': track_info['title'],
                        'duration': track_info['duration'],
                        'owner': youtube_service.user
                    }
                )
                print(f"Track {'criada' if created else 'encontrada'}: {track}")
                cleaned_data['track'] = track
            else:
                raise forms.ValidationError(_('Não foi possível obter informações da faixa'))

        except Exception as e:
            print(f"Erro ao processar faixa: {e}")
            raise forms.ValidationError(f'Erro ao processar faixa: {str(e)}')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if not self.cleaned_data.get('DELETE', False):
            instance.track = self.cleaned_data.get('track')
            instance.owner = self.request.user if hasattr(self, 'request') else None
        
            if commit:
                instance.save()
        
        return instance


class PlaylistTrackInline(InlineFormSetFactory):
    model = PlaylistTrack
    form_class = PlaylistTrackForm
    factory_kwargs = {
        'extra': 0,
        'can_delete': True,
        'can_order': True,
        'min_num': 0,
        'validate_min': False,
    }
    prefix = 'playlist_tracks'

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        print("Factory kwargs:", kwargs)
        return kwargs

    def construct_formset(self):
        formset = super().construct_formset()
        print("Constructed formset:", formset)
        for form in formset.forms:
            form.request = self.request
        return formset
