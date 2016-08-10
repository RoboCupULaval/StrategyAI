import unittest

from RULEngine.Util.Position import Position

class TestPosition(unittest.TestCase):

    def test_eq(self):
        pos1 = Position()
        pos2 = Position()

        pos3 = Position(500, 400)
        pos4 = Position(400, -400)
        pos5 = Position(-500, 400)

        pos6 = Position(0.5, 0)
        pos7 = Position(0, 0)
        pos8 = Position(1, 0)

        pos9 = Position(-0.5, 0)
        pos10 = Position(-1, 0)
        pos11 = Position(0, 0)

        self.assertEqual(pos1, pos2)
        self.assertEqual(pos2, pos1)

        self.assertFalse(pos3 == pos4)
        self.assertFalse(pos3 == pos5)
        self.assertFalse(pos3 == pos6)

        self.assertTrue(pos6 == pos7)
        self.assertFalse(pos6 == pos8)

        self.assertTrue(pos9 == pos10)
        self.assertFalse(pos9 == pos11)
