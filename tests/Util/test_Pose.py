import unittest

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

class TestPose(unittest.TestCase):

    def test_eq(self):
        pos1 = Pose()
        pos2 = Pose()
        pos3 = Pose(Position(500, 400), 0)
        pos4 = Pose(Position(500, 400), 1.5)
        pos5 = Pose(Position(500, 400), -1.5)
        pos6 = Pose(Position(400, 500), 0)

        self.assertEqual(pos1, pos2)
        self.assertEqual(pos2, pos1)

        self.assertFalse(pos3 == pos4)
        self.assertFalse(pos3 == pos5)
        self.assertFalse(pos3 == pos6)
