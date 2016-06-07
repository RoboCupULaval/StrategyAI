# Under MIT License, see LICENSE.txt
from unittest import TestCase
from AI.STP.Skill.sStop import sStop
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class TestSkillStop(TestCase):
    """ Tests de la classe sWait """
    def setUp(self):
        self.skill = sStop()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sStop)

    def test_name(self):
        self.assertEqual(self.skill.name, sStop.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target, self.goal)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Pose)
        self.assertEqual(result.orientation, self.bot_pos.orientation)
        self.assertEqual(result.position.x, self.bot_pos.position.x)
        self.assertEqual(result.position.y, self.bot_pos.position.y)
        self.assertEqual(result.position.z, self.bot_pos.position.z)
