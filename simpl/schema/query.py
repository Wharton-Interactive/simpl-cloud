import graphene

from .. import get_run_model
from . import types


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
            run = Run.objects.prefetch_related(
                "player_set__user", "lobby_set__player_set"
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
