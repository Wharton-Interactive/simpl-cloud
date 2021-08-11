from simpl.models import BaseRun
from django.test import TestCase
from django.apps import apps
from model_bakery import baker
from simpl import get_run_model, get_player_model


class RunTest(TestCase):
    def setUp(self):
        Player = get_player_model()
        self.simpl_run = baker.make(get_run_model(), game__name="Game")
        self.players = baker.make(
            Player, run=self.simpl_run, user__first_name="Julia", _quantity=3
        )
        self.player_inactive = baker.make(Player, run=self.simpl_run, inactive=True)

    def make_lobbies(self):
        lobbies = baker.make("simpl.Lobby", run=self.simpl_run, ready=True, _quantity=2)
        lobbies[0].player_set.add(self.players[0], self.player_inactive)
        lobbies[1].player_set.add(self.players[1], self.players[2])
        baker.make("simpl.Lobby", run=self.simpl_run, ready=False)
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
        player = baker.make(get_player_model(), run=run)
        self.assertEqual(run.instance_set.count(), 0)

        run.status = run.STATUS.PLAY
        player = baker.make(get_player_model(), run=run)
        self.assertEqual(run.instance_set.count(), 1)
        player.refresh_from_db()
        instance = run.instance_set.get()
        self.assertEqual(player.character.instance, instance)
        self.assertEqual(instance.status, instance.STATUS.PLAY)
