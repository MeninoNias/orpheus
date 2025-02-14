# Generated by Django 5.1.6 on 2025-02-14 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloader', '0002_add_default_platform'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='platform',
            options={'ordering': ['name'], 'verbose_name': 'Plataforma', 'verbose_name_plural': 'Plataformas'},
        ),
        migrations.AddField(
            model_name='platform',
            name='active',
            field=models.BooleanField(default=True, help_text='Indica se a plataforma está ativa para uso', verbose_name='Ativo'),
        ),
        migrations.AddField(
            model_name='platform',
            name='logo',
            field=models.URLField(blank=True, help_text='URL do logo da plataforma', verbose_name='Logo'),
        ),
        migrations.AlterField(
            model_name='platform',
            name='base_url',
            field=models.URLField(blank=True, help_text='URL base da plataforma (ex: https://youtube.com)', verbose_name='URL Base'),
        ),
        migrations.AlterField(
            model_name='platform',
            name='name',
            field=models.CharField(help_text='Nome da plataforma (ex: YouTube, SoundCloud)', max_length=50, unique=True, verbose_name='Nome'),
        ),
        migrations.AddIndex(
            model_name='platform',
            index=models.Index(fields=['name'], name='downloader__name_8f26d1_idx'),
        ),
    ]
