import graphene

from . import mutations, query
from .external import mutations as external_mutations
from .external.query import Query as ExternalQuery


class Mutation(graphene.ObjectType):
    balance_teams = mutations.BalanceTeams.Field()
    alter_player = mutations.AlterPlayer.Field()

    run = external_mutations.SimplRun.Field()
    players = external_mutations.SimplPlayers.Field()
    managers = external_mutations.SimplManagers.Field()
    class_ = external_mutations.SimplClass.Field(name="class")


class Query(query.Query, ExternalQuery):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
