# Under MIT license, see LICENSE.txt

from ai.STA.Action.Move_to import Move_to
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.InfoManager import InfoManager
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
import unittest

class TestActions(unittest.TestCase):
    def setUp(self):
        # ToDo : Use mock instead of actual objects
        self.info_manager = InfoManager()
        self.player_id = 1 # random integer

    def test_move_to(self):
        self.pose = Pose(Position(0,0,0),orientation = 0.0)
        self.move = Move_to(self.info_manager, self.player_id, self.pose)
        self.assertEqual(str(Move_to.exec(self.move)),
                         "AICommand(move_destination=[(x=0.0, y=0.0, z=0.0), theta=0.0], kick_strength=0)")

        self.pose = Pose(Position(0.5, 0.3, 0.2), orientation=3.2)
        self.move = Move_to(self.info_manager, self.player_id, self.pose)
        self.assertEqual(str(Move_to.exec(self.move)),
                         "AICommand(move_destination=[(x=0.5, y=0.3, z=0.2), theta=-3.083185307179586], kick_strength=0)")

    def test_idle(self):
        self.idle = Idle(self.info_manager,self.player_id)
        current_pose = self.info_manager.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0)"
        self.assertEqual(str(Idle.exec(self.idle)),current_pose_string)

    def test_kick(self):

        # test avec la valeur 0 (nulle)
        self.kick = Kick(self.info_manager,self.player_id,0)
        current_pose = self.info_manager.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0)"
        self.assertEqual(str(Kick.exec(self.kick)),current_pose_string)

        # test avec la valeur 1 (force maximale)
        self.kick = Kick(self.info_manager, self.player_id, 1)
        current_pose = self.info_manager.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=1)"
        self.assertEqual(str(Kick.exec(self.kick)), current_pose_string)

        # test avec la valeur 0.3 (force intermediaire)
        self.kick = Kick(self.info_manager, self.player_id, 0.3)
        current_pose = self.info_manager.get_player_pose(self.player_id)
        current_pose_string = "AICommand(move_destination=" + str(current_pose) + ", kick_strength=0.3)"
        self.assertEqual(str(Kick.exec(self.kick)), current_pose_string)

if __name__ == "__main__":
    unittest.main()