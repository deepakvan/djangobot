from django.apps import AppConfig
import threading

class KuberConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kuber'

def ready(self):
    from .views import bot
    threading.Thread(target=bot).start()



