# shops/apps.py
from django.apps import AppConfig

class ShopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shops'

    # Tambahkan method ini
    def ready(self):
        import shops.signals