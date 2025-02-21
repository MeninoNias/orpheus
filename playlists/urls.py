from django.urls import path
from .views import (
    PlaylistListView, PlaylistDetailView,
    PlaylistCreateView, PlaylistUpdateView, SearchTrackView
)

app_name = 'playlists'

urlpatterns = [
    path('', PlaylistListView.as_view(), name='list'),
    path('new/', PlaylistCreateView.as_view(), name='create'),  # mudado de 'create' para 'new'
    path('<int:pk>/', PlaylistDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', PlaylistUpdateView.as_view(), name='update'),
    path('search-tracks/', SearchTrackView.as_view(), name='search_tracks'),
]