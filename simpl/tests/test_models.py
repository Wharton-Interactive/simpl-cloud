import uuid
from allauth.socialaccount.models import SocialAccount

from django.apps import apps
from django.test import TestCase
from model_bakery import baker
from simpl import get_game_experience_model, get_player_model, get_run_model
from simpl.models import Lobby
from django.contrib.auth import get_user_model


class RunTest(TestCase):
    def setUp(self):
        Player = get_player_model()
        self.simpl_run = baker.make(get_run_model(), game__name="Game")
        self.players = baker.make(
            Player, run=self.simpl_run, user__first_name="Julia", _quantity=3
        )
        self.player_inactive = baker.make(Player, run=self.simpl_run, inactive=True)

    def make_lobbies(self):
        lobbies = baker.make("simpl.Lobby", run=self.simpl_run, _quantity=2)
        lobbies[0].player_set.add(self.players[0], self.player_inactive)
        lobbies[1].player_set.add(self.players[1], self.players[2])
        baker.make("simpl.Lobby", run=self.simpl_run)
        return lobbies

    def test_prepare_multiplayer_run(self):
        lobbies = self.make_lobbies()

        instances = self.simpl_run.prepare()

        self.assertEqual(len(instances), 2)
        for index, instance in enumerate(instances):
            self.assertEqual(instance.game, self.simpl_run.game)
            self.assertEqual(instance.run, self.simpl_run)
            lobby = lobbies[index]
            self.assertEqual(instance.name, lobby.name)
            characters = instance.character_set.all()
            lobby_players = lobby.player_set.active()
            self.assertEqual(characters.count(), lobby_players.count())
            for player in lobby_players:
                self.assertIn(player.character, characters)
                self.assertEqual(player.character.user, player.user)

    def test_prepare_single_player_run(self):
        self.simpl_run.multiplayer = False
        self.simpl_run.save()

        instances = self.simpl_run.prepare()

        self.assertEqual(len(instances), 3)
        for index, instance in enumerate(instances):
            self.assertEqual(instance.game, self.simpl_run.game)
            self.assertEqual(instance.run, self.simpl_run)
            characters = instance.character_set.all()
            self.assertEqual(characters.count(), 1)
            character = characters.first()
            player = self.simpl_run.player_set.get(character=character)
            self.assertEqual(character.user, player.user)

    def test_multiplayer_prepare(self):
        lobbies = self.make_lobbies()

        instances = self.simpl_run.prepare()

        self.assertEqual(len(instances), 2)
        for index, instance in enumerate(instances):
            self.assertEqual(instance.game, self.simpl_run.game)
            self.assertEqual(instance.run, self.simpl_run)
            lobby = lobbies[index]
            self.assertEqual(instance.name, lobby.name)
            characters = instance.character_set.all()
            lobby_players = lobby.player_set.active()
            self.assertEqual(characters.count(), lobby_players.count())
            for player in lobby_players:
                self.assertIn(player.character, characters)
                self.assertEqual(player.character.user, player.user)

    def test_single_player_prepare(self):
        self.simpl_run.multiplayer = False
        self.simpl_run.save()

        instances = self.simpl_run.prepare()

        self.assertEqual(len(instances), 3)
        for index, instance in enumerate(instances):
            self.assertEqual(instance.game, self.simpl_run.game)
            self.assertEqual(instance.run, self.simpl_run)
            characters = instance.character_set.all()
            self.assertEqual(characters.count(), 1)
            character = characters.first()
            player = self.simpl_run.player_set.get(character=character)
            self.assertEqual(character.user, player.user)

    def test_continuous_configurable(self):
        non_game_run = baker.make(get_run_model())
        self.assertEqual(
            non_game_run.continuous_configurable,
            apps.get_app_config("simpl").CONTINUOUS_CONFIGURABLE,
        )

        game_run_with_continuous_set = baker.make(
            get_run_model(), game__continuous=False
        )
        self.assertEqual(game_run_with_continuous_set.continuous_configurable, False)

        game_run_without_continuous_set = baker.make(
            get_run_model(), game__continuous=None
        )
        self.assertEqual(game_run_without_continuous_set.continuous_configurable, True)

    def test_continuous(self):
        run = baker.make(get_run_model(), continuous=True)
        player = baker.make(get_player_model(), run=run, user__username="p1")
        self.assertEqual(run.instance_set.count(), 0)

        run.status = run.STATUS.PLAY
        run.save()
        player = baker.make(get_player_model(), run=run, user__username="p2")
        self.assertEqual(run.instance_set.count(), 1)
        instance = run.instance_set.get()
        self.assertEqual(player.character.instance, instance)
        self.assertEqual(instance.status, instance.STATUS.PLAY)

    def test_version_sorting(self):
        GameExperience = get_game_experience_model()
        grouped_id = uuid.uuid4()
        for version in ["1.9", "1.10-copy", "1.10", "1.10a1", ""]:
            baker.make(GameExperience, experience_id=grouped_id, version=version)
        stand_alone_game = baker.make(
            GameExperience, experience_id=uuid.uuid4(), version="1.5"
        )
        non_experience_id_game = baker.make(
            GameExperience, experience_id=None, version="2"
        )

        games = GameExperience._default_manager.from_experience_id(grouped_id)
        self.assertEqual(
            [game.version for game in games], ["1.10a1", "", "1.10-copy", "1.9", "1.10"]
        )

        self.assertFalse(games[0].is_latest)
        self.assertTrue(games[-1].is_latest)

        self.assertTrue(stand_alone_game.is_latest)
        self.assertTrue(non_experience_id_game.is_latest)


class LobbyTestCase(TestCase):
    def test_ready(self):
        Player = get_player_model()
        baker.make(Lobby, name="empty")
        lobby2 = baker.make(Lobby, name="mixed")
        baker.make(Player, lobby=lobby2, ready=True, _quantity=2)
        baker.make(Player, lobby=lobby2, ready=False)
        lobby3 = baker.make(Lobby, name="ready")
        baker.make(Player, lobby=lobby3, ready=True, _quantity=2)
        lobby4 = baker.make(Lobby, name="unready")
        baker.make(Player, lobby=lobby4, ready=False, _quantity=2)
        self.assertEqual(set(Lobby.objects.ready()), {lobby3})

    def test_ready_queries(self):
        lobby = baker.make(Lobby)
        self.assertNumQueries(1)
        self.assertFalse(lobby.ready)
        self.assertNumQueries(2)

        annotated_lobby = Lobby.objects.prepare_ready().get()
        self.assertNumQueries(3)
        self.assertFalse(annotated_lobby.ready)
        self.assertNumQueries(3)


class SocialAccountTestCase(TestCase):
    def test_updates_user(self):
        user = baker.make(get_user_model())
        SocialAccount.objects.create(
            extra_data={"first_name": "Bob", "family_name": "Jones"}, user=user
        )
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Bob")
        self.assertEqual(user.last_name, "Jones")

    def test_updates_user(self):
        user = baker.make(get_user_model())
        SocialAccount.objects.create(extra_data={}, user=user)
        user_refreshed = get_user_model().objects.get()
        self.assertEqual(user.first_name, user_refreshed.first_name)
        self.assertEqual(user.last_name, user_refreshed.last_name)

    def test_sets_user_email_if_empty(self):
        user = baker.make(get_user_model(), email="")
        SocialAccount.objects.create(extra_data={"email": "new@example.com"}, user=user)
        user.refresh_from_db()
        self.assertEqual(user.email, "new@example.com")

    def test_dont_update_user_email(self):
        user = baker.make(get_user_model(), email="old@example.com")
        SocialAccount.objects.create(extra_data={"email": "new@example.com"}, user=user)
        user_refreshed = get_user_model().objects.get()
        self.assertEqual(user.email, user_refreshed.email)
