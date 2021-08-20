import json
from unittest import mock
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from simpl import get_run_model
from simpl.models import APIToken, Class, Run
from simpl.schema import schema


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


class ClassMutationTestCase(TestCase):
    def test_add_class(self):
        class_id = str(uuid.uuid4())
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        result = schema.execute(
            """mutation ($id: UUID!, $name: String!) {
                class(id: $id, name: $name)
            }""",
            variable_values={"id": class_id, "name": "Test class"},
            context_value=context,
        )
        self.assertEqual(result.data["class"], class_id)
        self.assertEqual(Class.objects.get().name, "Test class")

    def test_update_class(self):
        simpl_class = baker.make(Class)
        run = baker.make(Run, simpl_class=simpl_class)
        context = FakeContext()
        context.user = baker.make(get_user_model(), is_superuser=True)
        result = schema.execute(
            """mutation ($id: UUID!, $name: String!) {
                class(id: $id, name: $name)
            }""",
            variable_values={"id": simpl_class.id.hex, "name": "New name"},
            context_value=context,
        )
        self.assertEqual(result.data["class"], str(simpl_class.id))
        simpl_class.refresh_from_db()
        self.assertEqual(Class.objects.get().name, "New name")

        result = schema.execute(
            """
            query ($runId: ID!) {
                run(id: $runId) {
                    class
                }
            }""",
            variable_values={"runId": run.id},
            context_value=context,
        )
        self.assertEqual(result.data["run"]["class"], "New name")
