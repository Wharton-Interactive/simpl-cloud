from __future__ import annotations

import uuid
from typing import Union

from django.db import models
from django.db.models import Q
from django.db.models.expressions import Case, Value, When
from django.db.models.functions import Now
from packaging.version import parse


def _game_sort_key(game):
    version = parse(game.version)
    return not version.is_prerelease, version


class GameExperienceManager(models.Manager):
    def from_experience_id(self, experience_id: Union[uuid.UUID, str]):
        """
        Return a list of game experiences with the same experience_id, ordered
        from oldest to latest.
        """
        games = self.sort_games_by_version(
            self.filter(experience_id=experience_id).order_by("name")
        )
        for game in games:
            game.is_latest = game == games[-1]
        return games

    def sort_games_by_version(self, games):
        """
        Sorting considers valid pre-release versions to be oldest, then
        non-valid versions, then other valid versions. Here's an example list of
        experience versions sorted from oldest to latest:

        1. "1.10a1"
        2. ""
        3. "1.10-copy"
        4. "1.9
        5. "1.10"
        """
        games = list(games)
        games.sort(key=_game_sort_key)
        return games


class PlayerQuerySet(models.QuerySet):
    def unbalanced(self):
        return self.ready().filter(lobby=None)

    def active(self):
        return self.filter(inactive=False)

    def inactive(self):
        return self.filter(inactive=True)

    def ready(self):
        return (
            self.active()
            .has_user()
            .filter(character=None, ready=True)
            .select_related("user")
        )

    def has_user(self, value=True):
        return self.filter(user__isnull=not value)


class LobbyQuerySet(models.QuerySet):
    def empty(self, no_players: bool = True):
        qs = self.annotate(num_players=models.Count("player"))
        if no_players:
            return qs.filter(num_players=0)
        return qs.filter(num_players__gt=0)

    def availability(self, max_players: int = None, exclude_started=True):
        """
        Filter to only available lobbies.

        Pass a ``max_players`` integer to filter to lobbies with less players
        than this amount.

        Pass ``exclude_started=False`` if you don't want to exclude lobbies
        which already have a created instance.
        """
        qs = self
        if exclude_started:
            qs = self.alias(
                num_playing=models.Count("player", filter=~Q(player__character=None)),
            ).filter(num_playing=0)
        if max_players:
            qs = qs.annotate(num_available=max_players - models.Count("player")).filter(
                num_available__gt=0
            )
        return qs

    # Django <3.2 support
    def alias(self, *args, **kwargs):
        return getattr(super(), "alias", self.annotate)(*args, **kwargs)

    def prepare_ready(self):
        qs = self.annotate(player_count=models.Count("player"))
        qs = qs.alias(
            unready_players=models.Count(
                "player", filter=Q(player__character=None) & Q(player__ready=False)
            ),
        )
        return qs.annotate(
            ready=Case(
                When(player_count__gt=0, unready_players=0, then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
            not_ready=Case(
                When(unready_players__gt=0, then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
        )

    def ready(self, value: bool = True, include_linked: bool = False):
        """
        Filter to lobbies with at least one ready player, and no unready
        players.

        Checking for ``.ready(False)`` is not quite the inverse -- it will only
        include lobbies with at least one unready player.

        By default, both cases will only include lobbies not yet linked to an
        instance. Use ``include_linked=True`` to include all lobbies.
        """
        qs = self.filter(instance=None) if not include_linked else self.all()
        qs = qs.prepare_ready()
        if value:
            return qs.filter(ready=True)
        return qs.filter(not_ready=True)


class CharacterQuerySet(models.QuerySet):

    def annotate_status(self):
        # This should always be in sync with BaseCharacterData.status
        from .models import BaseCharacterData

        return self.annotate(
            _status=models.Case(
                models.When(
                    models.Q(_date_finished__lte=Now()) | models.Q(instance__date_end__lte=Now()),
                    then=BaseCharacterData.STATUS.COMPLETE,
                ),
                default=BaseCharacterData.STATUS.PLAY,
                output_field=models.PositiveSmallIntegerField(),
            ),
        )
