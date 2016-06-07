#Under MIT License, see LICENSE.txt
import unittest
from AI.STP.Play.pDemoGoalKeeper import *
from AI.STP.Play.pDemoGoalKeeper import pDemoGoalKeeper


class testPPathAxis(unittest.TestCase):
  def setUp(self):
    self.pDemoGoalKeeper = pDemoGoalKeeper()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_DEMO_GOAL_KEEPER, self.pDemoGoalKeeper.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_DEMO_GOAL_KEEPER, self.pDemoGoalKeeper.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pDemoGoalKeeper.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
