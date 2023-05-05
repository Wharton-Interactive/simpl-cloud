from django.db import models

from simpl import models as simpl_models


class World(simpl_models.BaseInstance):
    run = models.ForeignKey(
        simpl_models.Run, blank=True, null=True, on_delete=models.SET_NULL
    )


class WorldWithRelatedName(simpl_models.BaseInstance):
    run = models.ForeignKey(
        simpl_models.Run,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="worldswithrelatedname",
    )


class MyPlayer(simpl_models.BasePlayer):
    pass


class PlayerWithRelatedName(simpl_models.BaseInstance):
    run = models.ForeignKey(
        simpl_models.Run,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="playerswithrelatedname",
    )
