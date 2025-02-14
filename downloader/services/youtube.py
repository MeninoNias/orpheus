import yt_dlp
from .services import PlatformService
from ..models import Plataform

class YouTubeService(PlatformService):
    def download_audio(self, url, user):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'outtmpl': f'media/tracks/{user.id}/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3')
            
            artist, _ = Artist.objects.get_or_create(
                name=info['uploader'],
                platform=Platform.objects.get(name='YouTube'),
                user=user
            )

            return Track(
                title=info['title'],
                artist=artist,
                platform=Platform.objects.get(name='YouTube'),
                url=url,
                duration=info['duration'],
                audio_file=filename,
                user=user
            )

    def get_artist_info(self, artist_id):
        # Implemente a busca de informações do artista no YouTube
        pass