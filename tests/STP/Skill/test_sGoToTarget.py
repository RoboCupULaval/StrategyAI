# Under MIT License, see LICENSE.txt
from unittest import TestCase
from UltimateStrat.STP.Skill.sGoToTarget import sGoToTarget
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class TestSkillGoToTarget(TestCase):
    """ Tests de la classe sGoToTarget """
    def setUp(self):
        self.skill = sGoToTarget()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sGoToTarget)

    def test_name(self):
        self.assertEqual(self.skill.name, sGoToTarget.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target.position, self.goal.position)
        result_hope = Pose(self.target.position, self.bot_pos.orientation)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Pose)
        self.assertEqual(result.orientation, result_hope.orientation)
        self.assertEqual(result.position, result_hope.position)
