#Under MIT License, see LICENSE.txt
import unittest
from AI.STP.Play.pDefense import *


class testPPathAxis(unittest.TestCase):
  def setUp(self):
    self.pDefense = pDefense()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_DEFENSE, self.pDefense.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_DEFENSE, self.pDefense.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pDefense.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
