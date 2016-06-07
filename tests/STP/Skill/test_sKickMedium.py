# Under MIT License, see LICENSE.txt
from unittest import TestCase
from AI.STP.Skill.sKickMedium import sKickMedium
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class TestSkillKickMedium(TestCase):
    """ Tests de la classe sKickMedium """
    def setUp(self):
        self.skill = sKickMedium()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sKickMedium)

    def test_name(self):
        self.assertEqual(self.skill.name, sKickMedium.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target, self.goal)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 3)
