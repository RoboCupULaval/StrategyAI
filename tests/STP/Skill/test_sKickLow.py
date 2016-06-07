# Under MIT License, see LICENSE.txt
from unittest import TestCase
from AI.STP.Skill.sKickLow import sKickLow
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class TestSkillKickLow(TestCase):
    """ Tests de la classe sKickLow """
    def setUp(self):
        self.skill = sKickLow()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sKickLow)

    def test_name(self):
        self.assertEqual(self.skill.name, sKickLow.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target, self.goal)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 2)
