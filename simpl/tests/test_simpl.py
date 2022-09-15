import json
from unittest import mock
import uuid

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from simpl import (
    get_run_model,
    get_player_model,
    get_character_model,
    get_instance_model,
    get_game_experience_model,
)
from simpl.models import APIToken, Class
from simpl.schema import schema


Run = get_run_model()
Player = get_player_model()
Character = get_character_model()
Instance = get_instance_model()
GameExperience = get_game_experience_model()


class FakeContext:
    pass


class AuthTestCase(TestCase):
    def setUp(self):
        self.api_url = reverse("simpl-api")

    def test_anon(self):
        request = self.client.post(
            self.api_url, '{"query": "{runs{id}}"}', content_type="application/json"
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(json.loads(request.content)["data"], {"runs": None})

    def test_auth(self):
        token = APIToken.objects.create()
        request = self.client.post(
            self.api_url,
            '{"query": "{runs{id}}"}',
            content_type="application/json",
            HTTP_AUTHORIZATION=token.token,
        )
        self.assertEqual(request.status_code, 200)
        self.assertEqual(json.loads(request.content)["data"], {"runs": []})


class PlayersMutationTestCase(TestCase):
    def test_add_player(self):
        run = baker.make(get_run_model())
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        with mock.patch(
            "simpl.schema.external.utils._get_user_data",
        ) as data_mock:
            data_mock.return_value = {"email": "tester@example.com"}
            schema.execute(
                """mutation ($run: ID!, $players: [ID]!) {
                    players(runId: $run, auth0Ids: $players) { id }
                }""",
                variable_values={"run": run.pk, "players": ["abc"]},
                context_value=context,
            )
        self.assertEqual(run.player_set.count(), 1)
        player = run.player_set.get()
        self.assertFalse(player.inactive)

    def test_add_player_inactive(self):
        run = baker.make(get_run_model())
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        with mock.patch(
            "simpl.schema.external.utils._get_user_data",
        ) as data_mock:
            data_mock.side_effect = lambda x: {
                "abc": {"email": "tester@example.com"},
                "xyz": {"email": "tester2@example.com"},
            }[x]
            schema.execute(
                """mutation ($run: ID!, $players: [ID]!, $inactivePlayers: [ID]) {
                    players(
                        runId: $run,
                        auth0Ids: $players,
                        auth0IdsInactive: $inactivePlayers
                    ) { id }
                }""",
                variable_values={
                    "run": run.pk,
                    "players": ["abc", "xyz"],
                    "inactivePlayers": ["xyz"],
                },
                context_value=context,
            )
        self.assertEqual(run.player_set.count(), 2)
        player = run.player_set.get(user__email="tester@example.com")
        player2 = run.player_set.get(user__email="tester2@example.com")
        self.assertFalse(player.inactive)
        self.assertTrue(player2.inactive)


class ManagersMutationTestCase(TestCase):
    def test_add_manager(self):
        run = baker.make(get_run_model())
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        with mock.patch(
            "simpl.schema.external.utils._get_user_data",
        ) as data_mock:
            data_mock.return_value = {"email": "tester@example.com"}
            schema.execute(
                """mutation ($run: ID!, $managers: [ID]!) {
                    managers(runId: $run, auth0Ids: $managers) { id }
                }""",
                variable_values={"run": run.pk, "managers": ["abc"]},
                context_value=context,
            )
        self.assertEqual(run.managers.count(), 1)

    def test_remove_manager(self):
        run = baker.make(get_run_model())
        run.managers.add(baker.make(get_user_model(), email="tester@example.com"))
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        with mock.patch(
            "simpl.schema.external.utils._get_user_data",
        ) as data_mock:
            data_mock.return_value = {"email": "tester@example.com"}
            schema.execute(
                """mutation ($run: ID!, $managersRemove: [ID]) {
                    managers(
                        runId: $run,
                        auth0IdsRemove: $managersRemove
                    ) { id }
                }""",
                variable_values={
                    "run": run.pk,
                    "managersRemove": ["abc"],
                },
                context_value=context,
            )
        self.assertFalse(run.managers.exists())


class ClassMutationTestCase(TestCase):
    def test_add_class(self):
        class_id = str(uuid.uuid4())
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        result = schema.execute(
            """mutation ($id: UUID!, $name: String!) {
                simplClass(id: $id, name: $name)
            }""",
            variable_values={"id": class_id, "name": "Test class"},
            context_value=context,
        )
        self.assertEqual(result.data["simplClass"], class_id)
        self.assertEqual(Class.objects.get().name, "Test class")

    def test_update_class(self):
        simpl_class = baker.make(Class)
        run = baker.make(Run, simpl_class=simpl_class)
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        result = schema.execute(
            """mutation ($id: UUID!, $name: String!) {
                simplClass(id: $id, name: $name)
            }""",
            variable_values={"id": simpl_class.id.hex, "name": "New name"},
            context_value=context,
        )
        self.assertEqual(result.data["simplClass"], str(simpl_class.id))
        simpl_class.refresh_from_db()
        self.assertEqual(Class.objects.get().name, "New name")

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    className
                }
            }""",
            variable_values={"runId": run.id},
            context_value=context,
        )
        self.assertEqual(result.data["run"]["className"], "New name")


class SimplUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(
            get_user_model(),
            email="tester@example.com",
            first_name="Bob",
            last_name="Dylan",
        )
        cls.account = baker.make(SocialAccount, user=cls.user)
        cls.simpl_run = baker.make(Run, status=Run.STATUS.PLAY)
        cls.instance = baker.make(Instance, run=cls.simpl_run, date_end=timezone.now())
        cls.character = baker.make(
            Character,
            user=cls.user,
            instance=cls.instance,
            _date_finished=timezone.now(),
        )
        cls.player = baker.make(
            Player, user=cls.user, character=cls.character, run=cls.simpl_run
        )

    def test_get_user(self):
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        with mock.patch(
            "simpl.schema.external.utils._get_user_data",
        ) as data_mock:
            data_mock.return_value = {"email": "tester@example.com"}
            result = schema.execute(
                """query ($auth0Id: ID!) {
                    user(auth0Id: $auth0Id) {
                        firstName
                        lastName
                        auth0Id
                        runs {
                            id
                            name
                            status
                            instance {
                                name
                                status
                                dateEnd
                                playerName
                                playerStatus
                                playerFinished
                            }
                        }
                    }
                }""",
                variable_values={"auth0Id": self.account.uid},
                context_value=context,
            )
            self.maxDiff = None
            self.assertEqual(
                result.data,
                {
                    "user": {
                        "firstName": self.user.first_name,
                        "lastName": self.user.last_name,
                        "auth0Id": self.account.uid,
                        "runs": [
                            {
                                "id": str(self.simpl_run.id),
                                "name": self.simpl_run.name,
                                "status": self.simpl_run.status.name,
                                "instance": {
                                    "name": self.instance.name,
                                    "status": self.instance.status.name,
                                    "dateEnd": self.instance.date_end.isoformat(),
                                    "playerName": self.character.name,
                                    "playerStatus": self.character.status.name,
                                    "playerFinished": self.character.date_finished.isoformat(),
                                },
                            },
                        ],
                    }
                },
            )


class SimplGameTestCase(TestCase):
    def test_get_game(self):
        game = baker.make(GameExperience, experience_id=uuid.uuid4())
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        result = schema.execute(
            """
            query ($gameId: UUID!) {
                game(id: $gameId) {
                    id
                    name
                    continuous
                    runs {
                        id
                    }
                }
            }""",
            variable_values={"gameId": str(game.experience_id)},
            context_value=context,
        )

        self.assertEqual(
            result.data,
            {
                "game": {
                    "id": str(game.experience_id),
                    "name": game.name,
                    "continuous": None,
                    "runs": [],
                }
            },
        )
