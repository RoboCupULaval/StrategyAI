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

        # on test les cas où la position est la même, mais l'orientation peut changer
        # les edge case d'orientation devraient tous être validés
        speed_self = uut(Pose())
        self.assertEqual(speed_self, Pose())
        speed_self_rotate1 = uut(Pose(Position(), math.pi/2))
        self.assertEqual(speed_self_rotate1, Pose(Position(), 2))
        speed_self_rotate2 = uut(Pose(Position(), math.pi))
        self.assertEqual(speed_self_rotate2, Pose(Position(), 2))
        speed_self_rotate3 = uut(Pose(Position(), 3*math.pi/2))
        self.assertEqual(speed_self_rotate3, Pose(Position(), -2))
        speed_self_rotate8 = uut(Pose(Position(), math.pi+ORIENTATION_ABSOLUTE_TOLERANCE))
        self.assertEqual(speed_self_rotate8, Pose(Position(), -2)) # test edge case transition rotation negative
        speed_self_rotate4 = uut(Pose(Position(), 0.20))
        self.assertEqual(speed_self_rotate4, Pose(Position(), 0.4))
        speed_self_rotate5 = uut(Pose(Position(), 0.19))
        self.assertEqual(speed_self_rotate5, Pose(Position(), 0.4))
        speed_self_rotate6 = uut(Pose(Position(), -0.20))
        self.assertEqual(speed_self_rotate6, Pose(Position(), -0.4))
        speed_self_rotate7 = uut(Pose(Position(), -0.19))
        self.assertEqual(speed_self_rotate7, Pose(Position(), -0.4))

        # on test les cas où la Position est éloigné et doit être modifié
        # l'orientation est ignorée
        speed_pose_I = uut(Pose(Position(900, 900), 0))
        self.assertEqual(speed_pose_I, Pose(Position(math.sqrt(2)/2, math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose_II = uut(Pose(Position(-900, 900), 0))
        self.assertEqual(speed_pose_II, Pose(Position(-math.sqrt(2)/2, math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose_III = uut(Pose(Position(-900, -900), 0))
        self.assertEqual(speed_pose_III, Pose(Position(-math.sqrt(2)/2, -math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose_IV = uut(Pose(Position(900, -900), 0))
        self.assertEqual(speed_pose_IV, Pose(Position(math.sqrt(2)/2, -math.sqrt(2)/2, abs_tol=1e-3), 0))
        speed_pose = uut(Pose(Position(1000, 300), 0))
        self.assertEqual(speed_pose, Pose(Position(0.957, 0.287, abs_tol=1e-3), 0))
        speed_pose = uut(Pose(Position(300, 1000), 0))
        self.assertEqual(speed_pose, Pose(Position(0.287, 0.957, abs_tol=1e-3), 0))
