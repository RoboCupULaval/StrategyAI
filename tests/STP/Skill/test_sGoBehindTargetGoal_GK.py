# Under MIT License, see LICENSE.txt
from unittest import TestCase
from UltimateStrat.STP.Skill.sGoBehindTargetGoal_GK import sGoBehindTargetGoal_GK
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import get_angle, get_distance
from RULEngine.Util.area import stayInsideCircle

__author__ = 'RoboCupULaval'


class TestSkillGoBehindTargetGoal_GK(TestCase):
    """ Tests de la classe sGoBehindTargetGoal_GK """
    def setUp(self):
        self.skill = sGoBehindTargetGoal_GK()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sGoBehindTargetGoal_GK)

    def test_name(self):
        self.assertEqual(self.skill.name, sGoBehindTargetGoal_GK.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target.position, self.goal.position)

        # Calcul de la prochaine pose du gardien de but
        dst_target_player = get_distance(self.goal.position, self.target.position)
        new_pose = Pose(self.target.position, get_angle(self.goal.position, self.target.position))
        new_pose.position = stayInsideCircle(new_pose.position, self.goal.position, dst_target_player / 2)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Pose)
        self.assertEqual(result.orientation, new_pose.orientation)
        self.assertEqual(result.position, new_pose.position)
