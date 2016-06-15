# Under MIT License, see LICENSE.txt
""" Module test pHalt """
import unittest
from ai.STP.Play.pHalt import pHalt, SEQUENCE_HALT

class testPPathAxis(unittest.TestCase):
    """ Class test pHalt """
    def setUp(self):
        self.pHalt = pHalt()

    def test_getTactics_with_no_args(self):
        self.assertEqual(SEQUENCE_HALT, self.pHalt.getTactics())

    def test_getTactics_with_index(self):
        self.assertEqual(SEQUENCE_HALT[0], self.pHalt.getTactics(0))

    def test_get_Tactics_with_invalid_index(self):
        self.assertRaises(IndexError, self.pHalt.getTactics, 6)

if __name__ == '__main__':
    unittest.main()
