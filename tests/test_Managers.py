# Under MIT License, see LICENSE.txt
import unittest

from RULEngine.GameDomainObjects.Game import Game
from RULEngine.GameDomainObjects.Referee import Referee
from RULEngine.Util.team_color_service import TeamColor, TeamColorService
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from ai.states.game_state import GameState
from ai.states.module_state import ModuleState


class TestGameStateManager(unittest.TestCase):
    """
        Teste les différentes fonctionnalités du GameStateManager
    """
    def setUp(self):
        self.game = Game()
        self.referee = Referee
        self.game.set_referee(self.referee)
        self.tcsvc = TeamColorService(TeamColor.BLUE)
        self.game_world_OK = ReferenceTransferObject(self.game)
        self.game_world_OK.set_team_color_svc(self.tcsvc)

        self.GameStateManager1 = GameState()
        self.GameStateManager2 = GameState()
        self.GameStateManager1.set_reference(self.game_world_OK)

    def test_singleton(self):
        """
            Teste si le Manager est un singleton,
             i.e. s'il ne peut y avoir qu'une seule instance du manager
        """
        self.assertTrue(self.GameStateManager1 is self.GameStateManager2)
        self.assertIs(self.GameStateManager1, self.GameStateManager2)

    def test_set_reference(self):
        self.GameStateManager1.set_reference(self.game_world_OK)
        self.assertIs(self.GameStateManager1.game.referee,
                      self.game_world_OK.game.referee)
        self.assertIs(self.GameStateManager1.field,
                      self.game_world_OK.game.field)
        self.assertIs(self.GameStateManager1.game.our_team_color,
                      self.game.our_team_color)

        game_state_manager = GameState()
        self.assertRaises(AssertionError,
                          game_state_manager.set_reference, None)
        game = Game()
        game_world_nok = ReferenceTransferObject(game)
        self.assertRaises(AssertionError,
                          game_state_manager.set_reference, game_world_nok)
        game_world_nok.game.set_referee(self.referee)
        self.assertRaises(AssertionError,
                          game_state_manager.set_reference, game_world_nok)
        game = Game()
        game_world_nok = ReferenceTransferObject(game)
        game_world_nok.set_team_color_svc(self.tcsvc)
        self.assertRaises(AssertionError,
                          game_state_manager.set_reference, game_world_nok)


class TestModuleManager(unittest.TestCase):
    def setUp(self):
        self.manager = ModuleState()

    def test_singleton(self):
        other_manager= ModuleState()
        self.assertTrue(self.manager is other_manager)
