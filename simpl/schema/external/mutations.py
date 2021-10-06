from typing import Sequence

import graphene
import graphql
from simpl import get_game_experience_model, get_run_model, models

from . import types
from .utils import get_auth0_users, simpl_token_required

GameExperience = get_game_experience_model()
Run = get_run_model()


class SimplRun(graphene.Mutation):
    """
    Create a new Simpl Run.
    """

    class Arguments:
        name = graphene.String(required=True)
        game_id = graphene.UUID()
        class_id = graphene.UUID()
        multiplayer = graphene.Boolean()
        continuous = graphene.Boolean()

    Output = types.SimplRun

    @staticmethod
    @simpl_token_required
    def mutate(
        root,
        info,
        name,
        game_id=None,
        class_id=None,
        multiplayer=False,
        continuous=False,
    ):
        if game_id:
            games = GameExperience._default_manager.from_experience_id(game_id)
            if not games:
                raise graphql.GraphQLError("No game found")
            game = games[-1]
        else:
            game = None
        simpl_class = models.Class.objects.get(id=class_id) if class_id else None
        run = Run.objects.create(
            name=name,
            game=game,
            simpl_class=simpl_class,
            multiplayer=multiplayer,
            continuous=continuous,
        )
        return run


class SimplClass(graphene.Mutation):
    """
    Create or update a Simpl Class.
    """

    class Arguments:
        id = graphene.UUID(required=True)
        name = graphene.String(required=True)

    Output = graphene.UUID

    @staticmethod
    @simpl_token_required
    def mutate(root, info, name, id):
        return models.Class.objects.update_or_create(id=id, defaults=dict(name=name))[
            0
        ].id


class SimplPlayers(graphene.Mutation):
    """
    Add Players to (or remove Players from) a Run.

    Can also mark players as in a Run, but inactive.

    Creates any users that don't already exist.
    """

    class Arguments:
        run_id = graphene.ID(required=True)
        auth0_ids = graphene.List(graphene.ID)
        auth0_ids_remove = graphene.List(graphene.ID)
        auth0_ids_inactive = graphene.List(graphene.ID)

    @staticmethod
    @simpl_token_required
    def mutate(
        root,
        info,
        run_id,
        auth0_ids: Sequence[str] = (),
        auth0_ids_remove: Sequence[str] = (),
        auth0_ids_inactive: Sequence[str] = (),
    ):
        run = Run.objects.get(pk=run_id)
        for user in get_auth0_users(*(set(auth0_ids) | set(auth0_ids_inactive))):
            inactive = user.auth0_id in auth0_ids_inactive
            player, created = run.player_set.get_or_create(
                user=user, defaults={"inactive": inactive}
            )
            if not created and player.inactive != inactive:
                started_game = (
                    player.character
                    and player.character.instance.status
                    >= models.BaseInstance.STATUS.PLAY
                )
                if not started_game:
                    player.inactive = inactive
                    player.save()

        remove_users = get_auth0_users(
            *auth0_ids_remove, create_users=False, update_user_data=False
        )
        if remove_users:
            run.player_set.filter(user__in=remove_users, character=None).delete()
            if not run.multiplayer:
                run.instance_set.filter(character__user__in=remove_users).delete()
        return run

    Output = types.SimplRun


class SimplManagers(graphene.Mutation):
    """
    Add or remove managers for a Run.
    """

    class Arguments:
        run_id = graphene.ID(required=True)
        auth0_ids = graphene.List(graphene.ID)
        auth0_ids_remove = graphene.List(graphene.ID)

    @staticmethod
    @simpl_token_required
    def mutate(root, info, run_id, auth0_ids=(), auth0_ids_remove=()):
        run = Run.objects.get(pk=run_id)
        add_users = get_auth0_users(*auth0_ids)
        if add_users:
            run.managers.add(*add_users)
        remove_users = get_auth0_users(
            *auth0_ids_remove, create_users=False, update_user_data=False
        )
        if remove_users:
            run.managers.remove(*remove_users)

    Output = types.SimplRun
