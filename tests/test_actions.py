# Under MIT license, see LICENSE.txt

from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from ai.STA.Action.GrabBall import GrabBall
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.MoveWithBall import MoveWithBall
from ai.InfoManager import InfoManager
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Game.Ball import Ball
import unittest
from math import pi, atan


class TestActions(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        self.info_manager = InfoManager()
        self.player_id = 1  # random integer
        self.ball = Ball()
        self.ball.set_position(Position(5, 0), 1)
        self.info_manager._update_ball(self.ball)

    def test_move_to(self):
        self.pose = Pose(Position(0, 0, 0), orientation=0.0)
        self.move = MoveTo(self.info_manager, self.player_id, self.pose)
        self.assertEqual(str(MoveTo.exec(self.move)),
                         "AICommand(move_destination=[(x=0.0, y=0.0, z=0.0), theta=0.0], kick_strength=0)")

        self.pose = Pose(Position(0.5, 0.3, 0.2), orientation=3.2)
        self.move = MoveTo(self.info_manager, self.player_id, self.pose)
        self.assertEqual(str(MoveTo.exec(self.move)),
                         "AICommand(move_destination=[(x=0.5, y=0.3, z=0.2), theta=-3.083185307179586], kick_strength=0)")

    def test_idle(self):
        self.idle = Idle(self.info_manager, self.player_id)
        current_pose = self.info_manager.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0)"
        self.assertEqual(str(Idle.exec(self.idle)), current_pose_string)

    def test_GrabBall(self):
        self.grab_ball = GrabBall(self.info_manager, self.player_id)
        self.assertEqual(str(self.grab_ball.exec()),
                         "AICommand(move_destination=[(x=5.0, y=0.0, z=0.0), theta=0.0], kick_strength=0)")

        self.ball.set_position(Position(-5, 5), 1)
        self.info_manager._update_ball(self.ball)
        self.assertEqual(str(self.grab_ball.exec()),
                         "AICommand(move_destination=[(x=-5.0, y=5.0, z=0.0), theta=" +
                         str(3*pi/4) + "], kick_strength=0)")

    def test_MoveWithBall(self):
        self.move_with_ball = MoveWithBall(self.info_manager, self.player_id, Position(100, 0))
        self.ball.set_position(Position(5, 0), 1)
        self.info_manager._update_ball(self.ball)
        self.assertEqual(str(self.move_with_ball.exec()),
                         "AICommand(move_destination=[(x=100.0, y=0.0, z=0.0), theta=0.0], kick_strength=0)")

        self.ball.set_position(Position(5, 2), 1)
        self.info_manager._update_ball(self.ball)
        self.assertEqual(str(self.move_with_ball.exec()),
                         "AICommand(move_destination=[(x=100.0, y=0.0, z=0.0), theta=" +
                         str(atan(2/5)) + "], kick_strength=0)")

    def test_GoBetween(self):
        pass

if __name__ == "__main__":
    unittest.main()
