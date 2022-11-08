from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, List, Optional, Tuple

import faker
from django.apps import apps
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from simpl.conf import settings
from simpl.utils.models import DataMixin
from simpl.utils.name_faker import random_name

from . import get_character_model, get_instance_model, managers

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

fake = faker.Faker()


class BaseGameExperience(models.Model):
    name = models.CharField(max_length=100)
    experience_id = models.UUIDField(db_index=True, blank=True, null=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    version = models.CharField(max_length=20, blank=True)
    multiplayer = models.BooleanField(
        blank=True,
        null=True,
        help_text="Whether multiple players play a single instance of the game. "
        "If unset, this becomes configurable at the run level.",
    )
    continuous = models.BooleanField(
        blank=True,
        null=True,
        help_text="Whether players can join after a run is in play. "
        "If unset, this becomes configurable at the run level.",
    )
    allow_facilitator_continuous_management = models.BooleanField(
        blank=True,
        null=True,
        default=True,
        help_text="Allow facilitators to disable enrollment for continuous runs. "
        "If unset, this becomes configurable at the run level.",
    )

    objects = managers.GameExperienceManager()
    _default_manager: managers.GameExperienceManager

    class Meta:
        abstract = True
        ordering = "-date_created"

    def __str__(self):
        if self.version:
            return f"{self.name} (v{self.version})"
        return self.name

    @staticmethod
    def new_instance_name():
        return " ".join(fake.words(3)).title()

    @cached_property
    def is_latest(self):
        if not self.experience_id:
            return True
        games = type(self)._default_manager.from_experience_id(self.experience_id)
        return self == games[-1] if games else True


class GameExperience(BaseGameExperience):
    """
    A specific Simpl experience.

    This is only required for projects that provide multiple different Simpl
    experiences.
    """

    class Meta:
        swappable = "SIMPL_GAME_EXPERIENCE"


class Class(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class BaseRun(DataMixin, models.Model):
    class STATUS(enum.IntEnum):
        SETUP = 0
        PREPARE = 1
        PLAY = 2
        DEBRIEF = 3
        COMPLETE = 4

    STATUS.do_not_call_in_templates = True

    STATUSES = (
        (STATUS.SETUP.value, "Setup"),
        (STATUS.PREPARE.value, "Players Prepare"),
        (STATUS.PLAY.value, "Play"),
        (STATUS.DEBRIEF.value, "Debrief"),
        (STATUS.COMPLETE.value, "Complete"),
    )

    game: Optional[GameExperience] = models.ForeignKey(
        settings.SIMPL_GAME_EXPERIENCE, on_delete=models.CASCADE, blank=True, null=True
    )
    simpl_class: Optional[Class] = models.ForeignKey(
        Class, on_delete=models.SET_NULL, blank=True, null=True
    )
    name = models.CharField(
        max_length=100, help_text="Name of the run, for administration use."
    )
    public_name = models.CharField(
        max_length=100, help_text="Publically visible name of the game."
    )
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=STATUS.SETUP)
    data: dict = JSONField(editable=False, default=dict, blank=True)
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="simpl_run_set",
        related_query_name="simpl_run",
    )
    multiplayer = models.BooleanField(default=True)
    continuous = models.BooleanField(
        default=False,
        help_text="Automatically add new players to new instances for runs in play.",
    )
    date_continuous_end = models.DateTimeField(blank=True, null=True)
    allow_facilitator_continuous_management = models.BooleanField(
        default=True,
        help_text="Allow facilitators to disable enrollment for continuous runs.",
    )

    date_prepare = None

    player_set: Player.PlayerRelatedManager
    lobby_set: Lobby.LobbyRelatedManager

    class Meta:
        abstract = True
        ordering = ("-date_created",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and self.game:
            if self.game.continuous is not None:
                self.continuous = self.game.continuous
            if self.game.multiplayer is not None:
                self.multiplayer = self.game.multiplayer
            if self.game.allow_facilitator_continuous_management is not None:
                self.allow_facilitator_continuous_management = (
                    self.game.allow_facilitator_continuous_management
                )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("simpl", kwargs={"pk": self.pk})

    @property
    def setting_up(self):
        return self.status == self.STATUS.SETUP

    @property
    def preparing(self):
        return self.status == self.STATUS.PREPARE

    @property
    def playing(self):
        return self.status == self.STATUS.PLAY

    @property
    def in_debrief(self):
        return self.status == self.STATUS.DEBRIEF

    @property
    def completed(self):
        return self.status == self.STATUS.COMPLETE

    def get_play_url(self):
        return ""

    @cached_property
    def instances(self):
        from simpl import get_instance_model

        Instance = get_instance_model()
        return Instance.objects.filter(run=self)

    @cached_property
    def running_instances(self) -> List[BaseInstance]:
        return [
            instance
            for instance in self.instances
            if instance.date_start and not instance.date_end
        ]

    @cached_property
    def ended_instances(self) -> List[BaseInstance]:
        return [instance for instance in self.instances if instance.date_end]

    @cached_property
    def ended(self):
        if self.completed:
            return True
        instances_count = len(self.instances)
        return instances_count > 0 and len(self.ended_instances) == instances_count

    def prepare(self) -> List[BaseInstance]:
        """
        Create instances for players that are ready to begin.

        For multiplayer games, creates instances for lobbies that are ready. For
        single player games, creates instances for unlinked players to this
        run.
        """
        if self.date_prepare and self.date_prepare > timezone.now():
            return []
        instances = []
        with transaction.atomic():
            if self.multiplayer:
                lobby: Lobby
                for lobby in self.lobby_set.ready(include_linked=True):
                    instance, created = self.create_multiplayer_instance_from_lobby(
                        lobby
                    )
                    if created:
                        instances.append(instance)
            else:
                for player in self.player_set.ready():
                    instance = self.create_singleplayer_instance(player)
                    instances.append(instance)
        return instances

    def create_multiplayer_instance_from_lobby(self, lobby):
        assert lobby.run == self and lobby.ready
        instance, created = self.get_or_create_multiplayer_instance(lobby)
        player: BasePlayer
        for player in lobby.player_set.ready():
            self.add_player_to_instance(player, instance)
        return instance, created

    def add_player_to_instance(self, player: BasePlayer, instance: BaseInstance):
        player.character = get_character_model().objects.create(
            instance=instance,
            user=player.user,
        )
        player.save()

    def get_or_create_multiplayer_instance(
        self, lobby: Lobby, defaults: dict = None
    ) -> Tuple[BaseInstance, bool]:
        defaults = defaults or {}
        if not "name" in defaults:
            defaults["name"] = lobby.name
        defaults["game"] = self.game
        instance, created = get_instance_model()._default_manager.get_or_create(
            run=self, lobby=lobby, defaults=defaults
        )
        if created:
            lobby.instance = instance
            lobby.save()
        return instance, created

    def create_singleplayer_instance(self, player: BasePlayer) -> BaseInstance:
        instance = get_instance_model()._default_manager.create(
            run=self, game=self.game
        )
        self.add_player_to_instance(player, instance)
        return instance

    def start_instances(self, instances: List[BaseInstance]):
        now = timezone.now()
        started = 0
        for instance in instances:
            if not instance.date_start:
                instance.date_start = now
                instance.save()
                started += 1
        return started

    def _get_app_setting(self, key):
        app_setting = getattr(apps.get_app_config("simpl"), key)
        if callable(app_setting):
            app_setting = app_setting(self)
        return app_setting

    @property
    def continuous_configurable(self) -> bool:
        if self.game:
            return self.game.continuous is None
        return self._get_app_setting("CONTINUOUS_CONFIGURABLE")

    @property
    def continuous_open(self) -> bool:
        """
        Whether the run is open for continuous runs.

        The run must be marked as continuous, in Play status, and without a
        date_continous_end in the past.
        """
        return (
            self.status == self.STATUS.PLAY
            and self.continuous
            and (
                not self.date_continuous_end
                or self.date_continuous_end > timezone.now()
            )
        )

    @property
    def use_status_prepare(self) -> bool:
        return self._get_app_setting("USE_STATUS_PREPARE")

    @property
    def use_status_debrief(self) -> bool:
        return self._get_app_setting("USE_STATUS_DEBRIEF")

    @property
    def can_end(self) -> bool:
        return self._get_app_setting("CAN_END_RUN")

    @property
    def can_restart(self) -> bool:
        return self.can_end and self._get_app_setting("CAN_RESTART_RUN")


class Run(BaseRun, DataMixin, models.Model):
    """
    One runthrough (of one or more game instances) of a Simpl experience.
    """

    objects: models.manager.Manager[Run]

    class Meta:
        swappable = "SIMPL_RUN"
        ordering = ("-date_created",)


class BaseInstance(DataMixin, models.Model):
    class STATUS(enum.IntEnum):
        WAITING = 1
        PREPARE = 2
        PLAY = 3
        DEBRIEF = 4
        COMPLETE = 5

    STATUS.do_not_call_in_templates = True

    @property
    def status(self):
        if self.date_end:
            return self.STATUS.COMPLETE
        if self.run:
            if self.run.status == BaseRun.STATUS.SETUP:
                return self.STATUS.WAITING
            if self.run.status == BaseRun.STATUS.DEBRIEF:
                return self.STATUS.DEBRIEF
            if self.run.status == BaseRun.STATUS.PREPARE:
                return self.STATUS.PREPARE
        if self.date_start:
            return self.STATUS.PLAY
        return self.STATUS.WAITING

    run: Optional[BaseRun] = models.ForeignKey(
        settings.SIMPL_RUN, on_delete=models.CASCADE, blank=True, null=True
    )
    game: Optional[GameExperience] = models.ForeignKey(
        settings.SIMPL_GAME_EXPERIENCE, on_delete=models.CASCADE, blank=True, null=True
    )
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    data: dict = JSONField(editable=False, default=dict, blank=True)

    class Meta:
        abstract = True
        ordering = ("-date_created",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            if self.run and self.run.game:
                self.name = self.run.game.new_instance_name()
            elif self.game:
                self.name = self.game.new_instance_name()
            else:
                self.name = GameExperience.new_instance_name()
        super().save(*args, **kwargs)

    @property
    def running(self) -> bool:
        return bool(self.date_start and not self.date_end)

    def stop(self):
        self.date_end = timezone.now()
        self.save()

    def restart(self):
        self.date_end = None
        self.save()

    def get_status_display(self):
        if not self.date_start:
            return "Unstarted"
        if not self.date_end:
            return "Play"
        return "Complete"

    def archive(self):
        self.player_set.delete()

    def get_play_url(self):
        return ""

    def finish_characters(self, *characters: BaseCharacterData):
        for character in characters:
            assert character.instance_id == self.id
            character.finish()

        all_characters = self.character_set.exclude(user=None)
        total = all_characters.count()
        finished = all_characters.exclude(_date_finished=None).count()
        if total and total == finished:
            self.date_end = timezone.now()
            self.save()


class Instance(BaseInstance):
    """
    An instance of a Simpl experience.
    """

    objects = managers.CharacterQuerySet.as_manager()

    class Meta:
        swappable = "SIMPL_INSTANCE"


class BaseCharacterData(DataMixin, models.Model):
    class STATUS(enum.IntEnum):
        PLAY = 1
        COMPLETE = 2

    name = models.CharField("In-game name", max_length=200)
    data: dict = JSONField(editable=False, default=dict, blank=True)
    _date_finished = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def date_finished(self):
        return self._date_finished

    @property
    def status(self):
        # This should always be in sync with managers.CharacterQuerySet.annotate_status
        now = timezone.now()
        if (self.date_finished and self.date_finished <= now) or (
            self.instance.date_end and self.instance.date_end <= now
        ):
            return self.STATUS.COMPLETE
        return self.STATUS.PLAY

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.get_default_name()
        super().save(*args, **kwargs)

    def get_default_name(self):
        other_characters = self._meta.model._default_manager.filter(
            instance=self.instance
        )
        if self.pk:
            other_characters = other_characters.exclude(pk=self.pk)
        return random_name(
            existing_names=other_characters.values_list("name", flat=True)
        )

    def finish(self):
        self._date_finished = timezone.now()
        self.save()


class BaseCharacterLinked(models.Model):
    instance: Instance = models.ForeignKey(
        settings.SIMPL_INSTANCE, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Character(BaseCharacterData, BaseCharacterLinked):
    """
    A character in the game.

    Only characters with :attr:`user` set, are considered player characters.
    """

    objects = managers.CharacterQuerySet.as_manager()

    class Meta:
        swappable = "SIMPL_CHARACTER"


class Lobby(models.Model):
    run: BaseRun = models.ForeignKey(settings.SIMPL_RUN, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    instance: Instance = models.ForeignKey(
        settings.SIMPL_INSTANCE, on_delete=models.SET_NULL, blank=True, null=True
    )

    objects = managers.LobbyQuerySet.as_manager()

    if TYPE_CHECKING:

        class LobbyRelatedManager(
            models.manager.RelatedManager["Lobby"],
            managers.LobbyQuerySet["Lobby"],
        ):
            ...

    player_set: Player.PlayerRelatedManager

    @cached_property
    def ready(self) -> Optional[bool]:
        if self.instance_id:
            return None  # Not ready because linked to an instance already.
        obj = Lobby.objects.prepare_ready().get(pk=self.pk)
        if obj.ready:
            return True
        if not obj.player_count:
            return None  # Not ready because there are no players.
        return False


class BasePlayer(models.Model):
    run: BaseRun = models.ForeignKey(settings.SIMPL_RUN, on_delete=models.CASCADE)
    ready = models.BooleanField(default=True)
    inactive = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    lobby: Optional[Lobby] = models.ForeignKey(
        Lobby, on_delete=models.SET_NULL, blank=True, null=True
    )
    character: Optional[Character] = models.ForeignKey(
        settings.SIMPL_CHARACTER, on_delete=models.SET_NULL, blank=True, null=True
    )
    completed = models.DateTimeField(blank=True, null=True)

    objects = managers.PlayerQuerySet.as_manager()

    if TYPE_CHECKING:

        class PlayerRelatedManager(
            models.manager.RelatedManager["Player"],
            managers.PlayerQuerySet["Player"],
        ):
            ...

    class Meta:
        abstract = True

    def __str__(self):
        if self.user:
            return self.user.get_full_name() or self.user.email or self.user.username
        if self.character:
            return str(self.character)
        return "<Player>"

    @property
    def public_name(self):
        name = self.user and self.user.get_full_name() or "Anonymous Player"
        if self.character:
            character = str(self.character)
            if character != name:
                name += f": {character}"
        return name

    @property
    def team_name(self):
        if self.run.multiplayer:
            if self.lobby:
                return self.lobby.name
            if self.character:
                return self.character.instance.name

    def get_play_url(self) -> str:
        custom_play_url = getattr(settings, "SIMPL_GET_PLAY_URL", None)
        if custom_play_url:
            return import_string(custom_play_url)(self)
        if self.character and self.character.instance:
            return self.character.instance.get_play_url()
        elif self.run:
            return self.run.get_play_url()
        return ""


class Player(BasePlayer):
    """
    A player linked to a run.
    """

    class Meta:
        swappable = "SIMPL_PLAYER"


class APIToken(models.Model):
    token = models.CharField(max_length=32, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=True)
    last_used = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name or self.token_part

    @property
    def token_part(self):
        return f"{self.token[:8]}..."

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)
