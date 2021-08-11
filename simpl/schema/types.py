import graphene
from graphene_django import DjangoObjectType

from .. import get_player_model, get_run_model, models

Player = get_player_model()
Run = get_run_model()


class BalancingPlayer(DjangoObjectType):
    name = graphene.String()
    email = graphene.String()
    session = graphene.String()

    class Meta:
        model = Player
        fields = ["id", "inactive"]

    @staticmethod
    def resolve_name(obj: Player, info):
        return str(obj)

    @staticmethod
    def resolve_email(obj: Player, info):
        if obj.user and obj.user.email != str(obj):
            return obj.user.email


class BalancingTeam(DjangoObjectType):
    name = graphene.String()
    players = graphene.List(graphene.ID)
    session = graphene.String()

    class Meta:
        model = models.Lobby
        fields = ["id"]

    @staticmethod
    def resolve_name(obj: models.Lobby, info):
        return obj.name

    @staticmethod
    def resolve_players(obj: models.Lobby, info):
        return [player.pk for player in obj.player_set.all()]


class Balancing(DjangoObjectType):
    class Meta:
        model = Run
        fields = []

    sessions = graphene.List(graphene.String)
    players = graphene.List(BalancingPlayer)
    teams = graphene.List(BalancingTeam)

    @staticmethod
    def resolve_players(obj, info):
        return obj.player_set.all()

    @staticmethod
    def resolve_teams(obj, info):
        return obj.lobby_set.all()
