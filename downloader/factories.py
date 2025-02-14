from .services.youtube import YouTubeService


class PlatformServiceFactory:
    @staticmethod
    def get_service(platform_name):
        if platform_name == 'YouTube':
            return YouTubeService()
        else:
            raise ValueError(f"Plataforma não suportada: {platform_name}")
