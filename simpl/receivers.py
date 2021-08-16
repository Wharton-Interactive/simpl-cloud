from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .models import BasePlayer


def start_continuous_singleplayer(instance: BasePlayer, **kwargs):
    if (
        not instance.character
        and instance.user
        and not instance.inactive
        and instance.ready
        and instance.run.status == instance.run.STATUS.PLAY
        and instance.run.continuous
    ):
        simpl_instance = instance.run.create_singleplayer_instance(instance)
        instance.run.start_instances([simpl_instance])
