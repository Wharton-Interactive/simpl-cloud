from __future__ import annotations

from django.db import models


class PlayerQuerySet(models.QuerySet):
    def unbalanced(self):
        return self.ready().filter(lobby=None)

    def active(self):
        return self.filter(inactive=False)

    def inactive(self):
        return self.filter(inactive=True)

    def ready(self):
        return self.active().has_user().filter(character=None, ready=True).select_related("user")

    def has_user(self, value=True):
        return self.filter(user__isnull=not value)


class LobbyQuerySet(models.QuerySet):
    def empty(self, no_players: bool = True):
        qs = self.annotate(num_players=models.Count("player"))
        if no_players:
            return qs.filter(num_players=0)
        return qs.filter(num_players__gt=0)

    def availability(self, max_players: int):
        num_available = max_players - models.Count("player")
        return self.annotate(num_available=num_available).filter(num_available__gt=0)

    def ready(self):
        return self.filter(ready=True)
