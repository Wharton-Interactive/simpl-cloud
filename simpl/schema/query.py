import graphene
from django.db.models import Prefetch

from simpl.models import Lobby
from .. import get_run_model, get_player_model
from . import types


Player = get_player_model()
Run = get_run_model()


class BalancingMixin:
    @staticmethod
    def get_user(info):
        user = getattr(info.context, "user", None)
        if user.is_authenticated:
            return user

    @classmethod
    def get_run(cls, info, run_id):
        user = cls.get_user(info)
        if not user:
            return None
        try:
            players_qs = Player.objects.select_related("user").order_by(
                "user__first_name", "user__last_name"
            )
            lobby_qs = Lobby.objects.prefetch_related(
                Prefetch("player_set", players_qs)
            ).prepare_ready().order_by("-date_created")
            run = Run.objects.prefetch_related(
                Prefetch("player_set", players_qs),
                Prefetch("lobby_set", lobby_qs)
            ).get(pk=run_id)
        except Run.DoesNotExist:
            return None
        return cls.check_run(user, run)

    @classmethod
    def check_run(cls, user, run):
        if not user.is_superuser and not run.managers.filter(pk=user.pk).exists():
            return None
        return run


class Query(BalancingMixin, graphene.ObjectType):
    balancing = graphene.Field(types.Balancing, run_id=graphene.ID())

    @classmethod
    def resolve_balancing(cls, root, info, run_id):
        return cls.get_run(info, run_id)
