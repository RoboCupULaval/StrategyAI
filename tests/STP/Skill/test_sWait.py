# Under MIT License, see LICENSE.txt
from unittest import TestCase
from UltimateStrat.STP.Skill.sWait import sWait

__author__ = 'RoboCupULaval'


class TestSkillWait(TestCase):
    """ Tests de la classe sWait """
    def setUp(self):
        self.skill = sWait()

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sWait)

    def test_name(self):
        self.assertEqual(self.skill.name, sWait.__name__)

    def test_return(self):
        result = self.skill.act(None, None, None)

        self.assertIsNone(result)
