#Under MIT License, see LICENSE.txt
from unittest import TestCase
from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'


class TestPlayBase(TestCase):
  def setUp(self):
    self.play_book = PlayBase()

  def test_getTactics(self):
    pass

  def test_getBook(self):
    self.assertIsInstance(self.play_book.getBook(), dict)
