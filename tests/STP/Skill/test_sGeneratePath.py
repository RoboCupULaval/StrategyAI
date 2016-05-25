# Under MIT License, see LICENSE.txt
from unittest import TestCase
from UltimateStrat.STP.Skill.sGeneratePath import sGeneratePath
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class TestSkillGeneratePath(TestCase):
    """ Tests de la classe sGeneratePath """
    def setUp(self):
        self.skill = sGeneratePath()
        self.target = Pose(Position(0, 0), 0)
        self.goal = Pose(Position(1, 1), 1)
        self.bot_pos = Pose(Position(2, 2), 2)

    def test_construction(self):
        self.assertNotEqual(self.skill, None)
        self.assertIsInstance(self.skill, sGeneratePath)

    def test_name(self):
        self.assertEqual(self.skill.name, sGeneratePath.__name__)

    def test_return(self):
        result = self.skill.act(self.bot_pos, self.target, self.goal)
        bot_angle = self.bot_pos.orientation
        result_hope = [Pose(Position(0, 0), bot_angle),
                        Pose(Position(0, 3000), bot_angle),
                        Pose(Position(3000, 3000), bot_angle),
                        Pose(Position(3000, 0), bot_angle),
                        Pose(Position(0, 0), bot_angle)
                        ]

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        for i, obj in enumerate(result):
            self.assertIsInstance(obj, Pose)
            self.assertEqual(obj.orientation, result_hope[i].orientation)
            self.assertEqual(obj.position, result_hope[i].position)
