# Under MIT licence, see LICENCE.txt

import unittest
from math import pi

from ai.Util.Raycast import *
from ai.states.game_state import GameState
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from RULEngine.GameDomainObjects.Referee import Referee
from RULEngine.Util.team_color_service import TeamColorService, TeamColor
from RULEngine.GameDomainObjects.Game import Game
from RULEngine.GameDomainObjects.Ball import Ball

__author__ = 'RoboCupULaval'


# TODO : Tester de façon plus exhaustive
class TestRaycast(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.game = Game()
        self.game.set_referee(Referee())
        self.game.ball = Ball()
        game_world = ReferenceTransferObject(self.game)
        game_world.set_team_color_svc(TeamColorService(TeamColor.YELLOW))
        self.game_state.set_reference(game_world)
        self.game_state.game.ball.set_position(Position(100, 0), 0)

    @unittest.skip("Fuck if i know, probably never used MGL 2017/06/28")
    def test_raycast(self):
        self.assertTrue(raycast(self.game_state, Position(100, 100), 200, -pi/2, BALL_RADIUS, [], [], False))

    def test_raycast2(self):
        pass

if __name__ == "__main__":
    unittest.main()
