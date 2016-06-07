#Under MIT License, see LICENSE.txt
import unittest
from ai.STP.Play.pPath import *

class testPPathAxis(unittest.TestCase):
  def setUp(self):
    self.pPath = pPath()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_PATH, self.pPath.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_PATH, self.pPath.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pPath.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
