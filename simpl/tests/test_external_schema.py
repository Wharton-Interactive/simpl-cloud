import uuid

import graphene
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase, override_settings
from model_bakery import baker

from simpl import (
    get_character_model,
    get_game_experience_model,
    get_instance_model,
    get_run_model,
)
from simpl.schema import schema
from simpl.schema.external import types

Run = get_run_model()
Instance = get_instance_model()
GameExperience = get_game_experience_model()
User = get_user_model()


class FakeContext:
    pass


class SimplInstanceTests(TransactionTestCase):
    """Test suite for Instances.
    Since the main Query does not define an `Instance` attribute, the instances are
    tested as part of a run.
    """

    def setUp(self):
        self.game = baker.make(GameExperience, experience_id=uuid.uuid4())
        self.run = baker.make(Run, game=self.game)
        self.context = FakeContext()
        self.context_user = baker.make(User, is_superuser=True)
        self.context.user = self.context_user

    def test_get_instance_info(self):
        instance = baker.make(Instance, run=self.run, _fill_optional=True)
        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    instances {
                        name
                        status
                        dateEnd
                        players
                        playerCount
                    }
                }
            }""",
            variable_values={"runId": self.run.id},
            context_value=self.context,
        )

        self.assertEqual(
            result.data,
            {
                "run": {
                    "instances": [
                        {
                            "dateEnd": instance.date_end.isoformat(),
                            "name": instance.name,
                            "status": instance.status.name,
                            "players": [],
                            "playerCount": 0,
                        },
                    ],
                }
            },
        )

    def test_get_instance_with_multiple_players(self):
        instance = baker.make(Instance, run=self.run)

        # Create users with Auth0 IDs
        user1 = baker.make(SocialAccount, provider="auth0", uid="auth0_1")
        user2 = baker.make(SocialAccount, provider="auth0", uid="auth0_2")

        # Create a user without an Auth0 ID
        user3 = baker.make(SocialAccount, provider="google", uid="google")

        # Create a user without SocialAccount
        user4 = baker.make(User)

        # Create characters linking the users to the instance
        baker.make("simpl.Character", instance=instance, user=user1.user)
        baker.make("simpl.Character", instance=instance, user=user2.user)
        baker.make("simpl.Character", instance=instance, user=user3.user)
        baker.make("simpl.Character", instance=instance, user=user4)

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    instances {
                        players
                        playerCount
                    }
                }
            }""",
            variable_values={"runId": self.run.id},
            context_value=self.context,
        )

        instance_data = result.data["run"]["instances"][0]

        # playerCount says there should be 4 players
        self.assertEqual(instance_data["playerCount"], 4)
        # However, there should be 2 players in `players`:
        self.assertEqual(len(instance_data["players"]), 2)
        # Users with Auth0 IDs should be in the list of players
        self.assertIn(user1.uid, instance_data["players"])
        self.assertIn(user2.uid, instance_data["players"])
        # Users without Auth0 IDs should not be in the list of players
        self.assertNotIn(user3.uid, instance_data["players"])
        # Users without SocialAccounts should not be in the list of players
        self.assertNotIn(user4.id, instance_data["players"])

    def test_number_of_queries_in_get_instance_with_multiple_players(self):
        instance = baker.make(Instance, run=self.run)
        n = 100

        # Create n users with Auth0 IDs
        users = []
        for i in range(n):
            users.append(baker.make(SocialAccount, provider="auth0", uid=f"auth0_{i}"))

        # Create characters linking the users to the instance
        for user in users:
            baker.make("simpl.Character", instance=instance, user=user.user)

        with self.assertNumQueries(5):
            result = schema.execute(
                """
                query ($runId: ID!) {
                    run(id: $runId) {
                        instances {
                            players
                            playerCount
                        }
                    }
                }""",
                variable_values={"runId": self.run.id},
                context_value=self.context,
            )

        instance_data = result.data["run"]["instances"][0]

        # There should be n players in playerCount
        self.assertEqual(instance_data["playerCount"], n)
        # There should be n players in `players`:
        self.assertEqual(len(instance_data["players"]), n)


@override_settings(
    SIMPL_INSTANCE="testapp.World", SIMPL_CHARACTER="testapp.MyCharacter"
)
class WorldInstanceTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from simpl.testapp.models import World

        class WorldStatus(graphene.Enum):
            class Meta:
                enum = World.STATUS

        class WorldType(types.SimplInstance):
            status = graphene.Field(WorldStatus)

            class Meta:
                model = World

        class WorldQuery(graphene.ObjectType):
            world = graphene.Field(
                WorldType,
                id=graphene.ID(required=True),
                description="Return the World for a given world ID.",
            )

            @staticmethod
            def resolve_world(root, info, id):
                try:
                    return World.objects.get(pk=id)
                except World.DoesNotExist:
                    return None

        cls.schema = graphene.Schema(query=WorldQuery)

        cls.game = baker.make(GameExperience, experience_id=uuid.uuid4())
        cls.simpl_run = baker.make(Run, game=cls.game)
        cls.context = FakeContext()
        cls.context_user = baker.make(User, is_superuser=True)
        cls.context.user = cls.context_user

        return super().setUpClass()

    def test_number_of_players_in_get_instance_with_world_class(self):
        World = get_instance_model()
        world = baker.make(World, run=self.simpl_run, name="My World")
        n = 250

        # Create n users with Auth0 IDs
        users = []
        for i in range(n):
            users.append(baker.make(SocialAccount, provider="auth0", uid=f"auth0_{i}"))

        # Create characters linking the users to the instance
        Character = get_character_model()
        for user in users:
            baker.make(Character, instance=world, user=user.user)

        with self.assertNumQueries(6):
            result = self.schema.execute(
                """
                query ($worldId: ID!) {
                    world(id: $worldId) {
                        players
                        playerCount
                    }
                }""",
                variable_values={"worldId": world.id},
                context_value=self.context,
            )

        instance_data = result.data["world"]

        # There should be n players in playerCount
        self.assertEqual(instance_data["playerCount"], n)
        # There should be n players in `players`:
        self.assertEqual(len(instance_data["players"]), n)


class SimplRunTests(TestCase):
    def setUp(self):
        self.game = baker.make(GameExperience, experience_id=uuid.uuid4())
        self.context = FakeContext()
        self.context_user = baker.make(User, is_superuser=True)
        self.context.user = self.context_user

    def test_get_run_info(self):
        c = baker.make("simpl.Class")
        run = baker.make(Run, game=self.game, simpl_class=c, _fill_optional=True)
        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    id
                    name
                    status
                    multiplayer
                    continuous
                    players
                    playerCount
                    managers
                    instances {
                        name
                    }
                    gameId
                    classId
                    className
                }
            }""",
            variable_values={"runId": run.id},
            context_value=self.context,
        )

        self.assertEqual(
            result.data,
            {
                "run": {
                    "id": str(run.id),
                    "name": run.name,
                    "status": run.status.name,
                    "multiplayer": run.multiplayer,
                    "continuous": run.continuous,
                    "players": [],
                    "playerCount": 0,
                    "managers": [],
                    "instances": [],
                    "gameId": str(run.game.experience_id),
                    "classId": str(c.id),
                    "className": c.name,
                }
            },
        )

    def test_run_resolve_players(self):
        run = baker.make(Run, game=self.game, _fill_optional=True)

        # Create user with Auth0 ID
        auth0_user = baker.make(SocialAccount, provider="auth0", uid="auth0")
        # Create user without Auth0 ID
        google_user = baker.make(SocialAccount, provider="google", uid="google")
        # Create user without SocialAccount
        regular_user = baker.make(User)

        # Create players:
        baker.make("simpl.Player", run=run, user=auth0_user.user)
        baker.make("simpl.Player", run=run, user=google_user.user)
        baker.make("simpl.Player", run=run, user=regular_user)

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    players
                    playerCount
                }
            }""",
            variable_values={"runId": run.id},
            context_value=self.context,
        )

        run_data = result.data["run"]

        # playerCount says there should be 3 players
        self.assertEqual(run_data["playerCount"], 3)
        # However, there should be 1 player in `players`:
        self.assertEqual(len(run_data["players"]), 1)
        # Players with Auth0 IDs should be in the list of players
        self.assertIn(auth0_user.uid, run_data["players"])
        # Users without Auth0 IDs should not be in the list of players
        self.assertNotIn(google_user.uid, run_data["players"])
        # Users without SocialAccounts should not be in the list of players
        self.assertNotIn(regular_user.id, run_data["players"])

    def test_run_resolve_players_unassigned(self):
        run = baker.make(Run, game=self.game)
        instance = baker.make(Instance, run=run)

        # Create two auth0 users
        auth0_user1 = baker.make(SocialAccount, provider="auth0", uid="auth0_1")
        auth0_user2 = baker.make(SocialAccount, provider="auth0", uid="auth0_2")
        auth0_user3 = baker.make(SocialAccount, provider="auth0", uid="auth0_3")

        # Create characters linking the users to the instance
        character_1 = baker.make(
            "simpl.Character", instance=instance, user=auth0_user1.user
        )
        character_2 = baker.make(
            "simpl.Character", instance=instance, user=auth0_user2.user
        )

        # Assign them to a player
        baker.make(
            "simpl.Player", run=run, user=auth0_user1.user, character=character_1
        )
        baker.make(
            "simpl.Player", run=run, user=auth0_user2.user, character=character_2
        )
        # Create a player without a character
        baker.make("simpl.Player", run=run, user=auth0_user3.user, character=None)

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    playersUnassigned
                }
            }""",
            variable_values={"runId": run.id},
            context_value=self.context,
        )

        run_data = result.data["run"]

        # Users assigned to a player should not be in list of playersUnassigned
        self.assertNotIn(auth0_user1.uid, run_data["playersUnassigned"])
        self.assertNotIn(auth0_user2.uid, run_data["playersUnassigned"])
        # Users not assigned to a player should be in list of playersUnassigned
        self.assertIn(auth0_user3.uid, run_data["playersUnassigned"])

    def test_run_resolve_players_inactive(self):
        run = baker.make(Run, game=self.game)

        # Create three auth0 users
        auth0_user1 = baker.make(SocialAccount, provider="auth0", uid="auth0_1")
        auth0_user2 = baker.make(SocialAccount, provider="auth0", uid="auth0_2")
        auth0_user3 = baker.make(SocialAccount, provider="auth0", uid="auth0_3")

        # Assign them to a player (two of them inactive)
        baker.make("simpl.Player", run=run, user=auth0_user1.user, inactive=True)
        baker.make("simpl.Player", run=run, user=auth0_user2.user, inactive=True)
        baker.make("simpl.Player", run=run, user=auth0_user3.user, inactive=False)

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    playersInactive
                }
            }""",
            variable_values={"runId": run.id},
            context_value=self.context,
        )

        run_data = result.data["run"]

        # Users that are inactive should be in list of playersInactive
        self.assertIn(auth0_user1.uid, run_data["playersInactive"])
        self.assertIn(auth0_user2.uid, run_data["playersInactive"])
        # Users that are active should not be in list of playersInactive
        self.assertNotIn(auth0_user3.uid, run_data["playersInactive"])

    def test_run_resolve_managers(self):
        run = baker.make(Run, game=self.game, _fill_optional=True)

        # Create user with Auth0 ID
        auth0_user = baker.make(SocialAccount, provider="auth0", uid="auth0")
        # Create user without Auth0 ID
        google_user = baker.make(SocialAccount, provider="google", uid="google")
        # Create user without SocialAccount
        regular_user = baker.make(User)

        # Link users to run as managers
        run.managers.add(auth0_user.user)
        run.managers.add(google_user.user)
        run.managers.add(regular_user)

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    managers
                }
            }""",
            variable_values={"runId": run.id},
            context_value=self.context,
        )

        run_data = result.data["run"]

        # Auth0 users should be in the list of managers
        self.assertIn(auth0_user.uid, run_data["managers"])
        # Users without Auth0 IDs should not be in the list of managers
        self.assertNotIn(google_user.uid, run_data["managers"])
        # Users without SocialAccounts should not be in the list of managers
        self.assertNotIn(regular_user.id, run_data["managers"])

    def test_run_resolve_instances(self):
        run = baker.make(Run, game=self.game)

        for _ in range(5):
            baker.make(Instance, run=run)

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    instances{
                        name
                    }
                }
            }""",
            variable_values={"runId": run.id},
            context_value=self.context,
        )

        instances = result.data["run"]["instances"]

        # There should be 5 instances
        self.assertEqual(len(instances), 5)

    def test_number_of_queries_with_multiple_instances_and_players(self):
        run = baker.make(Run, game=self.game)

        number_instances = 120
        number_players_per_instance = 5

        instances = []
        for _ in range(number_instances):
            instances.append(baker.make(Instance, run=run))

        # Create n users with Auth0 IDs
        users = []
        for i in range(number_players_per_instance):
            users.append(baker.make(SocialAccount, provider="auth0", uid=f"auth0_{i}"))

        # Create characters linking the users to the instance
        for instance in instances:
            for user in users:
                baker.make("simpl.Character", instance=instance, user=user.user)

        with self.assertNumQueries(5):
            result = schema.execute(
                """
                query ($runId: ID!) {
                    run(id: $runId) {
                        instances {
                            playerCount
                        }
                    }
                }""",
                variable_values={"runId": run.id},
                context_value=self.context,
            )

        self.assertEqual(len(result.data["run"]["instances"]), number_instances)
        self.assertEqual(
            result.data["run"]["instances"][0]["playerCount"],
            number_players_per_instance,
        )
