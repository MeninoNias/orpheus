from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from decouple import config


class OrpheusAdminSite(AdminSite):
    """
    Configuração personalizada do Admin do Django
    """
    # Configurações básicas
    site_title = config('ADMIN_SITE_TITLE', default='Orpheus')
    site_header = config('ADMIN_SITE_HEADER', default='Orpheus Admin')
    index_title = config('ADMIN_INDEX_TITLE', default='Painel de Controle')
    
    # Templates personalizados
    index_template = 'admin/custom_index.html'
    login_template = 'admin/custom_login.html'
    
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'version': config('VERSION', default='1.0.0'),
            'environment': config('ENVIRONMENT', default='development'),
        })
        return context


# Instancia o admin personalizado
admin_site = OrpheusAdminSite(name='admin')

# Substitui o admin padrão do Django
admin.site = admin_site

# Exporta o admin_site para uso em outros arquivos
default_site = admin_site
