import graphene
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from graphene import ResolveInfo
from graphql.language.ast import Field, Name
from model_bakery import baker

from simpl import (
    get_character_model,
    get_game_experience_model,
    get_instance_model,
    get_player_model,
    get_run_model,
)
from simpl.schema import schema
from simpl.schema.external import utils
from simpl.schema.external.types import SimplInstance

Run = get_run_model()
Instance = get_instance_model()
GameExperience = get_game_experience_model()
User = get_user_model()


class FakeContext:
    pass


class HasFieldNamedTests(TestCase):
    def test_can_find_field(self):
        info = ResolveInfo(
            field_name="players",
            field_asts=[Field(name=Name(value="players"))],
            return_type=graphene.ID(),
            parent_type=SimplInstance(),
            path=["run", "instances", 0, "players"],
            schema=schema,
            fragments={},
            root_value=None,
            operation=None,
            variable_values={"runId": "1"},
            context=FakeContext(),
        )

        self.assertTrue(utils.has_field_named(info, "players"))

    def test_can_find_field_in_multiple_fields(self):
        info = ResolveInfo(
            field_name="first_field",
            field_asts=[
                Field(name=Name(value="first_field")),
                Field(name=Name(value="second_field")),
                Field(name=Name(value="third_field")),
            ],
            return_type=graphene.ID(),
            parent_type=SimplInstance(),
            path=["run", "instances", 0, "first_field", "second_field", "third_field"],
            schema=schema,
            fragments={},
            root_value=None,
            operation=None,
            variable_values={"runId": "1"},
            context=FakeContext(),
        )

        self.assertTrue(utils.has_field_named(info, "first_field"))
        self.assertTrue(utils.has_field_named(info, "second_field"))
        self.assertTrue(utils.has_field_named(info, "third_field"))
        self.assertFalse(utils.has_field_named(info, "fourth_field"))

    def test_can_find_camelCase_field_in_multiple_fields(self):
        info = ResolveInfo(
            field_name="first_field",
            field_asts=[
                Field(name=Name(value="firstField")),
                Field(name=Name(value="secondField")),
                Field(name=Name(value="thirdField")),
            ],
            return_type=graphene.ID(),
            parent_type=SimplInstance(),
            path=["run", "instances", 0, "first_field", "second_field", "third_field"],
            schema=schema,
            fragments={},
            root_value=None,
            operation=None,
            variable_values={"runId": "1"},
            context=FakeContext(),
        )

        self.assertTrue(utils.has_field_named(info, "first_field"))
        self.assertTrue(utils.has_field_named(info, "second_field"))
        self.assertTrue(utils.has_field_named(info, "third_field"))
        self.assertFalse(utils.has_field_named(info, "fourth_field"))


class TestGetRunInstanceSetName(TestCase):
    def test_can_get_name_from_simpl_run_instance(self):
        instance_set_name = utils.get_run_instance_set_name()
        self.assertEqual(instance_set_name, "instance_set")

    @override_settings(SIMPL_INSTANCE="testapp.World")
    def test_can_get_name_from_testapp_world(self):
        instance_set_name = utils.get_run_instance_set_name()
        self.assertEqual(instance_set_name, "world_set")

    @override_settings(SIMPL_INSTANCE="testapp.WorldWithRelatedName")
    def test_can_get_name_from_testapp_world_with_related_name(self):
        instance_set_name = utils.get_run_instance_set_name()
        self.assertEqual(instance_set_name, "worldswithrelatedname")


class TestGetRunPlayerSetName(TestCase):
    def test_can_get_name_from_simpl_run_instance(self):
        player_set_name = utils.get_run_player_set_name()
        self.assertEqual(player_set_name, "player_set")

    @override_settings(SIMPL_PLAYER="testapp.MyPlayer")
    def test_can_get_name_from_testapp_myplayer(self):
        player_set_name = utils.get_run_player_set_name()
        self.assertEqual(player_set_name, "myplayer_set")

    @override_settings(SIMPL_PLAYER="testapp.PlayerWithRelatedName")
    def test_can_get_name_from_testapp_player_with_related_name(self):
        player_set_name = utils.get_run_player_set_name()
        self.assertEqual(player_set_name, "playerswithrelatedname")


class TestGetInstanceCharacterNames(TestCase):
    def test_can_get_name_from_simpl_instance(self):
        character_set_name = utils.get_instance_character_set_name()
        self.assertEqual(character_set_name, "character_set")
        character_query_name = utils.get_instance_character_query_name()
        self.assertEqual(character_query_name, "character")

    @override_settings(SIMPL_CHARACTER="testapp.MyCharacter")
    def test_can_get_name_from_testapp_myplayer(self):
        character_set_name = utils.get_instance_character_set_name()
        self.assertEqual(character_set_name, "mycharacter_set")
        character_query_name = utils.get_instance_character_query_name()
        self.assertEqual(character_query_name, "mycharacter")

    @override_settings(
        SIMPL_CHARACTER="testapp.CharacterWithRelatedName",
    )
    def test_can_get_name_from_testapp_player_with_related_name(self):
        character_set_name = utils.get_instance_character_set_name()
        self.assertEqual(character_set_name, "characters")
        character_query_name = utils.get_instance_character_query_name()
        self.assertEqual(character_query_name, "characters")


class TestGetRunInstances(TestCase):
    def test_can_get_instances_from_simpl_run(self):
        run = baker.make(Run)

        Instance = get_instance_model()
        instances = []
        for _ in range(3):
            instances.append(baker.make(Instance, run=run))

        other_run = baker.make(Run)
        other_instance = baker.make(Instance, run=other_run)

        instance_set = utils.get_run_instances(run)
        self.assertCountEqual(instances, instance_set)
        self.assertNotIn(other_instance, instance_set)

    @override_settings(SIMPL_INSTANCE="testapp.World")
    def test_can_get_instances_from_testapp_world(self):
        run = baker.make(Run)

        Instance = get_instance_model()
        instances = []
        for _ in range(3):
            instances.append(baker.make(Instance, run=run))

        instance_set = utils.get_run_instances(run)
        self.assertCountEqual(instances, instance_set)

    @override_settings(SIMPL_INSTANCE="testapp.WorldWithRelatedName")
    def test_can_get_name_from_testapp_world_with_related_name(self):
        run = baker.make(Run)

        Instance = get_instance_model()
        instances = []
        for _ in range(3):
            instances.append(baker.make(Instance, run=run))

        instance_set = utils.get_run_instances(run)
        self.assertCountEqual(instances, instance_set)


class TestGetRunPlayers(TestCase):
    def test_can_get_players_from_simpl_run(self):
        run = baker.make(Run)

        Player = get_player_model()
        players = []
        for _ in range(3):
            players.append(baker.make(Player, run=run))

        other_run = baker.make(Run)
        other_player = baker.make(Player, run=other_run)

        player_set = utils.get_run_players(run)
        self.assertCountEqual(players, player_set)
        self.assertNotIn(other_player, player_set)

    @override_settings(SIMPL_INSTANCE="testapp.MyPlayer")
    def test_can_get_players_from_testapp_myplayer(self):
        run = baker.make(Run)

        Player = get_player_model()
        players = []
        for _ in range(3):
            players.append(baker.make(Player, run=run))

        player_set = utils.get_run_players(run)
        self.assertCountEqual(players, player_set)

    @override_settings(SIMPL_INSTANCE="testapp.PlayerWithRelatedName")
    def test_can_get_players_from_testapp_player_with_related_name(self):
        run = baker.make(Run)

        Player = get_player_model()
        players = []
        for _ in range(3):
            players.append(baker.make(Player, run=run))

        player_set = utils.get_run_players(run)
        self.assertCountEqual(players, player_set)


class TestGetInstanceCharacters(TestCase):
    def _test(self):
        Instance = get_instance_model()
        instance = baker.make(Instance)

        User = get_user_model()
        users = []
        for _ in range(3):
            users.append(baker.make(User))

        # Link users to instance via character
        Character = get_character_model()
        characters = []
        for user in users:
            characters.append(baker.make(Character, user=user, instance=instance))

        character_set = utils.get_instance_characters(instance)
        self.assertCountEqual(characters, character_set)

    def test_can_get_characters_from_simpl_instance(self):
        self._test()

    @override_settings(
        SIMPL_INSTANCE="testapp.World", SIMPL_CHARACTER="testapp.MyCharacter"
    )
    def test_can_get_characters_from_world_and_mycharacter(self):
        self._test()

    @override_settings(
        SIMPL_INSTANCE="testapp.World",
        SIMPL_CHARACTER="testapp.CharacterWithRelatedName",
    )
    def test_can_get_characters_from_world_and_character_with_related_name(self):
        self._test()


class TestGetInstanceUsers(TestCase):
    def _test(self):
        Instance = get_instance_model()
        instance = baker.make(Instance)

        User = get_user_model()
        users = []
        for _ in range(3):
            users.append(baker.make(User))

        # Link users to instance via character
        Character = get_character_model()
        for user in users:
            baker.make(Character, user=user, instance=instance)

        user_set = utils.get_instance_users(instance)
        self.assertCountEqual(users, user_set)

    def test_can_get_users_from_simpl_instance(self):
        self._test()

    @override_settings(
        SIMPL_INSTANCE="testapp.World", SIMPL_CHARACTER="testapp.MyCharacter"
    )
    def test_can_get_users_from_world_and_mycharacter(self):
        self._test()

    @override_settings(
        SIMPL_INSTANCE="testapp.World",
        SIMPL_CHARACTER="testapp.CharacterWithRelatedName",
    )
    def test_can_get_users_from_world_and_character_with_related_name(self):
        self._test()
