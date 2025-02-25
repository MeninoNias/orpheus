import yt_dlp
from .services import PlatformService
from downloader.models import Platform
from playlists.models import Track, Artist

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
    
    def get_plataform(self):
        return Platform.objects.get_or_create(name='YouTube')[0]
    
    def get_track_info(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                print('TASDA', self.get_plataform())
                artist, _ = Artist.objects.get_or_create(
                    name=info.get('uploader', 'Unknown Artist'),
                    platform=self.get_plataform(),
                    owner=self.user
                )
                track_data = {
                    'title': info.get('title', 'Unknown Title'),
                    'artist': artist,
                    'platform': self.get_plataform(),
                    'url': url,
                    'duration': info.get('duration', 0),
                    'source_type': 'URL',
                    'thumbnail': info.get('thumbnails', [{'url': ''}])[0]['url']
                }
                return track_data
            except Exception as e:
                print(f"Error getting track info: {str(e)}")
                return None
    
    def search_faixa(self, faixa):
        faixas = []
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                results = ydl.extract_info(f'ytsearch5:{faixa}', download=False)
                
                if not results or 'entries' not in results:
                    return None
                
                for result in results['entries']:
                    artist, _ = Artist.objects.get_or_create(
                        name=result.get('uploader', 'Unknown Artist'),
                        platform=Platform.objects.get(name='YouTube'),
                        owner=self.user
                    )
                    track_data = {
                        'title': result.get('title', 'Unknown Title'),
                        'artist': artist.name,
                        'platform': 'YouTube',
                        'url': f"https://www.youtube.com/watch?v={result['id']}",
                        'duration': result.get('duration', 0),
                        'source_type': 'URL',
                        'thumbnail': result.get('thumbnails', [{'url': ''}])[0]['url']
                    }
                    faixas.append(track_data)

                return faixas
                
            except Exception as e:
                print(f"Error searching track: {str(e)}")
                return faixas