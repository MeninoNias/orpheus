from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.admin import default_site
from .models import Platform


@admin.register(Platform, site=default_site)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'base_url']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'base_url')
        }),
        (_('Informações do Sistema'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
