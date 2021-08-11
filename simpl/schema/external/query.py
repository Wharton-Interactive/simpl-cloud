from simpl import get_game_experience_model, get_run_model
from simpl.schema.external.utils import get_auth0_users, simpl_token_required
import graphene

from . import types

GameExperience = get_game_experience_model()
Run = get_run_model()

RUN_STATUSES = list(types.RunStatus._meta.enum.__members__)


class Query(graphene.ObjectType):
    user = graphene.Field(
        types.SimplUser,
        auth0_id=graphene.ID(required=True),
        description="Return the User for the given auth0 ID.\n\nDoes not create non-existant users.",
    )
    run = graphene.Field(
        types.SimplRun,
        id=graphene.ID(required=True),
        description="Return the Run for a given run ID.",
    )
    runs = graphene.List(
        types.SimplRun,
        statuses=graphene.List(types.RunStatus),
        game_id=graphene.ID(),
        description=f"Return all Runs. Can be filtered by game ID or runs in specific statuses.\n\nValid statuses are: {', '.join(RUN_STATUSES)}",
    )
    games = graphene.List(
        types.SimplGame,
        run_statuses=graphene.List(types.RunStatus),
        description=f"Return Game Experiences. Can be filtered to only those with runs in specific statuses.\n\nValid statuses are: {', '.join(RUN_STATUSES)}",
    )

    @staticmethod
    @simpl_token_required
    def resolve_user(root, info, auth0_id):
        users = get_auth0_users(auth0_id, create_users=False)
        if not users:
            return None
        user = users[0]
        user.auth0_id = auth0_id
        return user

    @staticmethod
    @simpl_token_required
    def resolve_run(root, info, id):
        try:
            return Run._default_manager.get(pk=id)
        except Run.DoesNotExist:
            return None

    @staticmethod
    @simpl_token_required
    def resolve_runs(root, info, statuses=(), game_id=None):
        runs = Run._default_manager.all()
        if statuses:
            runs = runs.filter(status__in=statuses)
        if game_id:
            runs = runs.filter(game=game_id)
        return runs

    @staticmethod
    @simpl_token_required
    def resolve_games(root, info, run_statuses=()):
        games = GameExperience._default_manager.all()
        if run_statuses:
            games = games.filter(run__status__in=run_statuses).distinct()
        return games
