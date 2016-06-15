#Under MIT License, see LICENSE.txt
import unittest
from ai.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'


class TestPlayBase(unittest.TestCase):
  def setUp(self):
    self.play_book = PlayBase()

  def test_getTactics(self):
    pass

  def test_getBook(self):
    self.assertIsInstance(self.play_book.getBook(), dict)


if __name__ == '__main__':
  unittest.main()