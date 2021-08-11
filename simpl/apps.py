from django.apps import AppConfig
from django.db.models.signals import post_save

from simpl import get_player_model, receivers


class SimplConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "simpl"
    CONTINUOUS_CONFIGURABLE = False

    def ready(self):
        post_save.connect(
            receivers.start_continuous_singleplayer, sender=get_player_model()
        )
