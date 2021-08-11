import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.module_loading import import_string
from graphene_django import DjangoObjectType
from simpl import get_game_experience_model, get_instance_model, get_run_model, models

from . import utils

User = get_user_model()
Instance = get_instance_model()
GameExperience = get_game_experience_model()
Run = get_run_model()
get_game_play_url = import_string(
    getattr(settings, "SIMPL_GET_GAME_PLAY_URL", "simpl.get_game_play_url")
)


class RunStatus(graphene.Enum):
    class Meta:
        enum = Run.STATUS


class InstanceStatus(graphene.Enum):
    class Meta:
        enum = models.BaseInstance.STATUS


class SimplInstance(DjangoObjectType):
    """
    A Simpl game instance
    """

    status = graphene.Field(InstanceStatus)
    players = graphene.List(
        graphene.ID, description="List of Auth0 IDs for players of this instance"
    )
    player_count = graphene.Int()

    class Meta:
        model = Instance
        skip_registry = True
        fields = ["name"]

    @staticmethod
    def resolve_status(obj, info):
        return obj.status

    @staticmethod
    def resolve_players(obj, info):
        users = User._default_manager.filter(character__instance=obj)
        return utils.get_auth0_ids(*users)

    @staticmethod
    def resolve_player_count(obj, info):
        return obj.character_set.exclude(user=None).count()


class SimplRun(DjangoObjectType):
    """
    A Simpl Run
    """

    management_url = graphene.String()
    players = graphene.List(
        graphene.ID, description="List of Auth0 IDs for players in this run"
    )
    players_unassigned = graphene.List(
        graphene.ID,
        description="List of Auth0 IDs for players that have not been assigned to a "
        "run yet.",
    )
    player_count = graphene.Int()
    managers = graphene.List(
        graphene.ID, description="List of Auth0 IDs for managers of this run"
    )
    instances = graphene.List(SimplInstance)
    status = graphene.Field(RunStatus)

    class Meta:
        model = Run
        skip_registry = True
        fields = ["id", "name", "multiplayer"]

    @staticmethod
    def resolve_management_url(obj, info):
        url = reverse("simpl", kwargs={"pk": obj.id})
        info.context.META
        return info.context.build_absolute_uri(url)

    @staticmethod
    def resolve_players(obj, info):
        users = User.objects.filter(player__run=obj)
        return utils.get_auth0_ids(*users)

    @staticmethod
    def resolve_players_unassigned(obj, info):
        users = User.objects.filter(player__run=obj, player__character=None)
        return utils.get_social_ids(*users)

    @staticmethod
    def resolve_player_count(obj, info):
        return obj.player_set.exclude(user=None).count()

    @staticmethod
    def resolve_managers(obj, info):
        return utils.get_auth0_ids(obj.managers.all())

    @staticmethod
    def resolve_instances(obj, info):
        return Instance._default_manager.filter(run=obj)


class SimplUserInstance(graphene.ObjectType):
    """
    A Simpl game instance, with information specific to a user
    """

    # Actually based on a Character model instance.
    name = graphene.String()
    status = graphene.Field(InstanceStatus)
    url = graphene.String()
    player_name = graphene.String()
    player_complete = graphene.Boolean()

    @staticmethod
    def resolve_name(obj, info):
        return obj.instance.name

    @staticmethod
    def resolve_status(obj, info):
        obj.instance.status

    @staticmethod
    def resolve_url(obj, info):
        url = get_game_play_url(user=obj.user, instance=obj.instance)
        if url:
            return info.context.build_absolute_uri(url)

    @staticmethod
    def resolve_player_name(obj, info):
        return obj.name

    @staticmethod
    def resolve_player_status(obj, info):
        if obj.instance.status >= models.BaseInstance.STATUS.DEBRIEF:
            return True
        return bool(obj.data.get("complete"))


class SimplUserRun(graphene.ObjectType):
    """
    A Simpl Run, with information specific to a user
    """

    # Actually based on a Player model instance.
    id = graphene.ID()
    name = graphene.String()
    status = graphene.Field(RunStatus)
    instance = graphene.Field(SimplUserInstance)
    url = graphene.String()

    @staticmethod
    def resolve_id(obj, info):
        return obj.run.pk

    @staticmethod
    def resolve_name(obj, info):
        return obj.run.name

    @staticmethod
    def resolve_status(obj, info):
        return obj.run.status

    @staticmethod
    def resolve_instance(obj, info):
        return obj.character

    @staticmethod
    def resolve_url(obj, info):
        url = get_game_play_url(user=obj.user, run=obj.run)
        if url:
            return info.context.build_absolute_uri(url)


class SimplUser(graphene.ObjectType):
    """
    A Simpl User
    """

    auth0_id = graphene.ID()
    runs = graphene.List(SimplUserRun)

    @staticmethod
    def resolve_auth0_id(obj, info):
        auth0_id = getattr(obj, "auth0_id", None)
        if auth0_id:
            return auth0_id
        try:
            return utils.get_auth0_ids(obj)[0]
        except IndexError:
            return None

    @staticmethod
    def resolve_runs(obj, info):
        return obj.player_set.select_related("run", "character__instance")


class SimplGame(DjangoObjectType):
    """
    A Simpl game experience
    """

    runs = graphene.List(SimplRun)

    class Meta:
        model = GameExperience
        skip_registry = True
        fields = ["id"]

    @staticmethod
    def resolve_runs(obj, info):
        return obj.run_set.all()
