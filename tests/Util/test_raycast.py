# Under MIT licence, see LICENCE.txt

import unittest
from math import pi

from ai.Util.Raycast import *
from ai.states.game_state import GameState
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from RULEngine.Game.Referee import Referee
from RULEngine.Util.team_color_service import TeamColorService, TeamColor
from RULEngine.Game.Game import Game
from RULEngine.Game.Ball import Ball
from config.config_service import ConfigService

__author__ = 'RoboCupULaval'


# TODO : Tester de façon plus exhaustive
class TestRaycast(unittest.TestCase):
    def setUp(self):
        config_service = ConfigService().load_file("config/sim_standard.cfg")
        self.game_state = GameState()
        self.game = Game()
        self.game.set_referee(Referee())
        self.game.ball = Ball()
        game_world = ReferenceTransferObject(self.game)
        game_world.set_team_color_svc(TeamColorService(TeamColor.YELLOW_TEAM))
        self.game_state.set_reference(game_world)
        self.game_state.game.ball.set_position(Position(100, 0), 0)

    def test_raycast(self):
        self.assertTrue(raycast(self.game_state, Position(100, 100), 200, -pi/2, BALL_RADIUS, [], [], False))

    def test_raycast2(self):
        pass

if __name__ == "__main__":
    unittest.main()
