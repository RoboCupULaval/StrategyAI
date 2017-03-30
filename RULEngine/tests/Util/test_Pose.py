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

        pos7 = Pose(Position(), 1.54679)
        pos8 = Pose(Position(), 1.54671)
        pos9 = Pose(Position(), 1.5466)
        pos10 = Pose(Position(), 1.5468)

        self.assertEqual(pos1, pos2)
        self.assertEqual(pos2, pos1)

        self.assertFalse(pos3 == pos4)
        self.assertFalse(pos3 == pos5)
        self.assertFalse(pos3 == pos6)

        self.assertTrue(pos7 == pos8)
        self.assertFalse(pos7 == pos9)
        self.assertFalse(pos7 == pos10)

    def test_to_tuple(self):
        uut = Pose()
        #sanity check
        self.assertNotEqual(type(uut.to_tuple()), type(Pose()))
        self.assertEqual(type(uut.to_tuple()), type(tuple()))

        self.assertEqual(uut.to_tuple(), tuple((0, 0)))

        uut = Pose(Position(557, -778.5), 0)
        self.assertEqual(uut.to_tuple(), tuple((557, -778.5)))
        self.assertNotEqual(uut.to_tuple(), tuple((-42, 3897)))
