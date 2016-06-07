# Under MIT License, see LICENSE.txt
from unittest import TestCase
from AI.STP.Skill.sFollowTarget import sFollowTarget
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import get_angle

__author__ = 'RoboCupULaval'


class TestSkillFollowTarget(TestCase):
    """ Tests de la classe sGoToTarget """
    def setUp(self):
        self.skill = sFollowTarget()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sFollowTarget)

    def test_name(self):
        self.assertEqual(self.skill.name, sFollowTarget.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target.position, self.goal.position)
        angle = get_angle(self.bot_pos.position, self.target.position)
        result_hope = Pose(self.target.position, angle)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Pose)
        self.assertEqual(result.orientation, result_hope.orientation)
        self.assertEqual(result.position, result_hope.position)
