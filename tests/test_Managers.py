# Under MIT License, see LICENSE.txt
import unittest

from RULEngine.services.team_color_service import TeamColor, TeamColorService
from ai.GameDomainObjects import Game
from ai.GameDomainObjects import Referee


class TestGameStateManager(unittest.TestCase):
    """
        Teste les différentes fonctionnalités du GameStateManager
    """
    def setUp(self):
        self.game = Game()
        self.referee = Referee
        self.game.set_referee(self.referee)
        self.tcsvc = TeamColorService(TeamColor.BLUE)

        self.GameStateManager1 = Game()
        self.GameStateManager2 = Game()

    def test_singleton(self):
        """
            Teste si le Manager est un singleton,
             i.e. s'il ne peut y avoir qu'une seule instance du manager
        """
        self.assertTrue(self.GameStateManager1 is self.GameStateManager2)
        self.assertIs(self.GameStateManager1, self.GameStateManager2)
