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
        widget=forms.HiddenInput()
    )

    class Meta:
        model = PlaylistTrack
        fields = ['track_url', 'position']
        widgets = {
            'position': forms.HiddenInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        track_url = cleaned_data.get('track_url')
        
        print('cleaned_data', cleaned_data)

        if not track_url or self.cleaned_data.get('DELETE', False):
            return cleaned_data

        try:
            youtube_service = YouTubeService()
            youtube_service.user = self.instance.playlist.user if self.instance.playlist else self.instance.owner
            track_info = youtube_service.get_track_info(track_url)

            if track_info:
                track, created = Track.objects.get_or_create(
                    url=track_info['url'],
                    defaults={
                        'title': track_info['title'],
                        'duration': track_info['duration'],
                        'owner': youtube_service.user
                    }
                )
                cleaned_data['track'] = track
            else:
                raise forms.ValidationError(
                    _('Não foi possível obter informações da faixa'))

        except Exception as e:
            raise forms.ValidationError(f'Erro ao processar faixa: {str(e)}')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.track = self.cleaned_data['track']
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
    fields = ['track_url', 'position']

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        kwargs.update(self.factory_kwargs)
        return kwargs
