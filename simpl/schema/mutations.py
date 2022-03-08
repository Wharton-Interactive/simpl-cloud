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

        lobbies = dict((str(team.pk), team) for team in run.lobby_set.all())
        run_players = dict((str(player.pk), player) for player in run.player_set.all())

        all_team_players: set[Player] = set()
        if teams:
            for team_input in teams:
                if delete_teams and team_input.id in delete_teams:
                    continue
                if team_input.id:
                    lobby = lobbies.get(team_input.id)
                    if not lobby:
                        continue
                else:
                    lobby = models.Lobby(run=run)
                cls.save_lobby_data(lobby, team_input)
                players = {run_players[pk] for pk in team_input.players if pk in run_players}
                lobby.player_set.set(players)
                all_team_players |= players
        inactive_team_players = [player.pk for player in all_team_players if player.inactive]
        if inactive_team_players:
            Player.objects.filter(pk__in=inactive_team_players).update(inactive=False)

        if delete_teams:
            run.lobby_set.filter(pk__in=delete_teams).delete()

        # Get the object (with prefetches) fresh from the DB.
        return cls.get_run(info, run_id)

    @staticmethod
    def save_lobby_data(lobby: models.Lobby, team: TeamInput, save: bool = True):
        lobby.name = team.name
        if save:
            lobby.save()
        return lobby


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
