# Under MIT License, see LICENSE.txt
from unittest import TestCase
from ai.STP.Skill.sNull import sNull
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class TestSkillNull(TestCase):
    """ Tests de la classe sNull """
    def setUp(self):
        self.skill = sNull()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sNull)

    def test_name(self):
        self.assertEqual(self.skill.name, sNull.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target, self.goal)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Pose)
        self.assertEqual(result.orientation, self.bot_pos.orientation)
        self.assertEqual(result.position, self.bot_pos.position)
