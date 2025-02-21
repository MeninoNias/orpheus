from abc import ABC, abstractmethod

class PlatformService(ABC):
    @abstractmethod
    def download_audio(self, url, user):
        pass

    @abstractmethod
    def get_artist_info(self, artist_id):
        pass
    
    @abstractmethod
    def search_faixa(self, faixa):
        pass