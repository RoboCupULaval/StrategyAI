# Under MIT License, see LICENSE.txt
import unittest
import math
import functools

from RULEngine.Command.command import _Command
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import ORIENTATION_ABSOLUTE_TOLERANCE

class TestCommand(unittest.TestCase):

    def test_convert_position_to_speed(self):
        # test incomplet très certainement
        cmd = _Command(Player(None, 0))
        current_pose = Pose()
        # uut est la fonction avec l'argument de la current_pose déjà établi, on peut appeler cette 'nouvelle' fonction en ne passant que le dernier paramètre
        # fyi: uut -> unit under test
        uut = functools.partial(cmd._convertPositionToSpeed, current_pose)

        target_pose_self = Pose()
        target_pose_self_rotate1 = Pose(Position(), math.pi/2)
        target_pose_self_rotate2 = Pose(Position(), math.pi)
        target_pose_self_rotate3 = Pose(Position(), 3*math.pi/2)
        target_pose_self_rotate4 = Pose(Position(), 0.2)
        target_pose_self_rotate5 = Pose(Position(), 0.19)
        target_pose_self_rotate6 = Pose(Position(), -0.2)
        target_pose_self_rotate7 = Pose(Position(), -0.19)
        target_pose_self_rotate8 = Pose(Position(), math.pi+ORIENTATION_ABSOLUTE_TOLERANCE)

        # position dans quadrant I
        target_pose_I = Pose(Position(900, 900))

        # position dans quandrant III
        target_pose_III = Pose(Position(-900, -900))

        # on test les cas où la position est la même, mais l'orientation peut changer
        # les edge case d'orientation devraient tous être validés
        speed_self = uut(target_pose_self)
        self.assertEqual(speed_self, Pose())
        speed_self_rotate1 = uut(target_pose_self_rotate1)
        self.assertEqual(speed_self_rotate1, Pose(Position(), 2))
        speed_self_rotate2 = uut(target_pose_self_rotate2)
        self.assertEqual(speed_self_rotate2, Pose(Position(), 2))
        speed_self_rotate3 = uut(target_pose_self_rotate3)
        self.assertEqual(speed_self_rotate3, Pose(Position(), -2))
        speed_self_rotate8 = uut(target_pose_self_rotate8)
        self.assertEqual(speed_self_rotate8, Pose(Position(), -2)) # test edge case transition rotation negative
        speed_self_rotate4 = uut(target_pose_self_rotate4)
        self.assertEqual(speed_self_rotate4, Pose(Position(), 0.4))
        speed_self_rotate5 = uut(target_pose_self_rotate5)
        self.assertEqual(speed_self_rotate5, Pose(Position(), 0.4))
        speed_self_rotate6 = uut(target_pose_self_rotate6)
        self.assertEqual(speed_self_rotate6, Pose(Position(), -0.4))
        speed_self_rotate7 = uut(target_pose_self_rotate7)
        self.assertEqual(speed_self_rotate7, Pose(Position(), -0.4))

        # on test les cas où la Position est éloigné et doit être modifié
        # l'orientation est ignorée
        speed_pose_I = uut(target_pose_I)
        self.assertEqual(speed_pose_I, Pose(Position(0, 0, abs_tol=1e-3), 0))
