from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import ListView

from .models import Platform


@method_decorator(cache_page(60 * 15), name='dispatch')  # Cache por 15 minutos
class PlatformListView(ListView):
    """
    View para listar plataformas ativas com estatísticas.
    """
    model = Platform
    template_name = 'downloader/index.html'
    context_object_name = 'platforms'

    def get_queryset(self):
        """Retorna apenas plataformas ativas com contagem de tracks."""
        return Platform.objects.all().annotate(
            tracks_count=Count('track')
        ).order_by('name')

    def get_context_data(self, **kwargs):
        """Adiciona dados extras ao contexto."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _('Downloader'),
            'total_platforms': cache.get_or_set(
                'total_platforms',
                Platform.objects.filter(active=True).count(),
                60 * 15  # 15 minutos
            ),
        })
        return context
