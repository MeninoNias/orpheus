from django.urls import path
from .views import PlatformListView

app_name = 'downloader'

urlpatterns = [
    path('', PlatformListView.as_view(), name='index'),
]