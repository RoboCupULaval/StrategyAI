import unittest

from RULEngine.Util.Position import Position

class TestPosition(unittest.TestCase):

    def test_eq(self):
        # les tests sont fait avec la tolérance par défaut défini dans position.py
        self.assertFalse(Position(900, 900) == Position())  # sanity check
        pos1 = Position()
        pos2 = Position()
        self.assertEqual(pos1, pos2)
        self.assertEqual(pos2, pos1)

        pos3 = Position(500, 400)
        pos4 = Position(400, -400)
        pos5 = Position(-500, 400)
        pos6 = Position(0.5, 0)
        self.assertFalse(pos3 == pos4)
        self.assertFalse(pos3 == pos5)
        self.assertFalse(pos3 == pos6)

        pos7 = Position(0.5, 0, abs_tol=1)
        pos8 = Position(0, 0, abs_tol=1)
        pos9 = Position(1, 0, abs_tol=1)
        self.assertTrue(pos7 == pos8)
        self.assertTrue(pos7 == pos9)

        pos10 = Position(0.5, 0, abs_tol=1)
        pos11 = Position(-0.5, 0, abs_tol=1)
        pos12 = Position(1, 0, abs_tol=1)
        self.assertTrue(pos10 == pos11)
        self.assertTrue(pos10 == pos12)

        # test pour voir si la tolérance est respectée
        pos11.abs_tol = 0.1
        pos10.abs_tol = 0.1
        self.assertFalse(pos11 == pos10)
        self.assertFalse(pos10 == pos11)
