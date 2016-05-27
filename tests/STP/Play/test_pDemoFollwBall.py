#Under MIT License, see LICENSE.txt
import unittest
from UltimateStrat.STP.Play.pDemoFollowBall import *


class testPPathAxis(unittest.TestCase):
  def setUp(self):
    self.pDemoFollowBall = pDemoFollowBall()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_DEMO_FOLLOW_BALL, self.pDemoFollowBall.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_DEMO_FOLLOW_BALL, self.pDemoFollowBall.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pDemoFollowBall.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
