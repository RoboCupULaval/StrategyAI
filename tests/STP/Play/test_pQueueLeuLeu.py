#Under MIT License, see LICENSE.txt
import unittest
from ai.STP.Play.pQueueLeuLeu import *

class TestPQueueLeuLeu(unittest.TestCase):
  def setUp(self):
    self.pTestQueueLeuLeu = pQueueLeuLeu()

  def test_getTactics_with_no_args(self):
    self.assertEqual(SEQUENCE_QUEUELEULEU, self.pTestQueueLeuLeu.getTactics())

  def test_getTactics_with_index(self):
      self.assertEqual(SEQUENCE_QUEUELEULEU, self.pTestQueueLeuLeu.getTactics(0))

  def test_get_Tactics_with_invalid_index(self):
      self.assertRaises(IndexError, self.pTestQueueLeuLeu.getTactics, 6)

if __name__ == '__main__':
  unittest.main()
