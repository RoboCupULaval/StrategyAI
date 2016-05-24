#Under MIT License, see LICENSE.txt
import unittest
from UltimateStrat.STP.Play.pTestBench import *

class testPTestBench(unittest.TestCase):
  def setUp(self):
    self.pTestBench = pTestBench()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_TEST_BENCH, self.pTestBench.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_TEST_BENCH, self.pTestBench.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pTestBench.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
