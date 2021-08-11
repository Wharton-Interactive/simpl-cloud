import graphene
import graphql

from .. import get_player_model, models
from . import query, types

Player = get_player_model()


class TeamInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String(required=True)
    session = graphene.String()
    players = graphene.List(graphene.ID, required=True)


class BalanceTeams(query.BalancingMixin, graphene.Mutation):
    class Arguments:
        run_id = graphene.ID(required=True)
        teams = graphene.List(TeamInput)
        delete_teams = graphene.List(graphene.ID)

    Output = types.Balancing

    @classmethod
    def mutate(cls, root, info, run_id, teams=None, delete_teams=None):
        run = cls.get_run(info, run_id)
        if not run:
            raise graphql.GraphQLError(message="Permission denied")

        run_teams = dict((str(team.pk), team) for team in run.lobby_set.all())
        run_players = dict((str(player.pk), player) for player in run.player_set.all())

        if teams:
            for team in teams:
                if delete_teams and team.id in delete_teams:
                    continue
                if team.id:
                    run_team = run_teams.get(team.id)
                    if not run_team:
                        continue
                else:
                    run_team = models.Lobby(run=run)
                run_team.name = team.name
                run_team.save()
                run_team.player_set.set(
                    [run_players[pk] for pk in team.players if pk in run_players]
                )

        if delete_teams:
            run.lobby_set.filter(pk__in=delete_teams).delete()

        # Get the object (with prefetches) fresh from the DB.
        return cls.get_run(info, run_id)


class AlterPlayer(query.BalancingMixin, graphene.Mutation):
    class Arguments:
        player_id = graphene.ID(required=True)
        active = graphene.Boolean(required=True)

    Output = types.BalancingPlayer

    @classmethod
    def mutate(cls, root, info, player_id, active):
        user = cls.get_user(info)
        run = None
        if user:
            try:
                player = Player.objects.get(pk=player_id)
            except Player.DoesNotExist:
                pass
            else:
                run = cls.check_run(user, player.run)
        if not run:
            raise graphql.GraphQLError(message="Permission denied")
        if player.inactive == active:
            player.inactive = not active
            player.save()
        return player
