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
        game_id=graphene.UUID(),
        description=f"Return all Runs. Can be filtered by game ID and/or runs in specific statuses.\n\nValid statuses are: {', '.join(RUN_STATUSES)}",
    )
    games = graphene.List(
        types.SimplGame,
        description=f"Return Game Experiences.",
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
            runs = runs.filter(game__experience_id=game_id)
        return runs

    @staticmethod
    @simpl_token_required
    def resolve_games(root, info):
        games = []
        current_experience_id = None
        current_group = []
        for game in (
            GameExperience._default_manager.exclude(experience_id=None)
            .order_by("experience_id")
            .iterator()
        ):
            if game.experience_id != current_experience_id:
                if current_group:
                    games.append(
                        GameExperience._default_manager.sort_games_by_version(
                            current_group
                        )[-1]
                    )
                    current_group = []
                current_experience_id = game.experience_id
            current_group.append(game)
        if current_group:
            games.append(
                GameExperience._default_manager.sort_games_by_version(current_group)[-1]
            )
        return games
