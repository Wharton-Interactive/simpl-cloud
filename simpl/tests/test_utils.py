import graphene
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from graphene import ResolveInfo
from graphql.language.ast import Field, Name

from simpl import get_game_experience_model, get_instance_model, get_run_model
from simpl.schema import schema
from simpl.schema.external.types import SimplInstance
from simpl.schema.external import utils

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
