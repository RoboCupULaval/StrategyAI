#Under MIT License, see LICENSE.txt
import unittest
from UltimateStrat.STP.Play.pHalt import *

class testPPathAxis(unittest.TestCase):
  def setUp(self):
    self.pHalt = pHalt()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_HALT, self.pHalt.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_HALT, self.pHalt.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pHalt.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
