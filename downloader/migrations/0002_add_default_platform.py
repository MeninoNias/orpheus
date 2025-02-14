from django.db import migrations


def add_default_platform(apps, schema_editor):
    Platform = apps.get_model('downloader', 'Platform')

    # Verifica se já existe uma plataforma YouTube
    if not Platform.objects.filter(name='YouTube').exists():
        Platform.objects.create(
            name='YouTube',
            base_url='https://youtube.com',
        )


def remove_default_platform(apps, schema_editor):
    Platform = apps.get_model('downloader', 'Platform')
    Platform.objects.filter(name='YouTube').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('downloader', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_platform, remove_default_platform),
    ]
