import math as m
from UltimateStrat.STP.Skill.SkillBase import SkillBase
from PythonFramework.Util.Pose import Pose, Position
from PythonFramework.Util.area import *
__author__ = 'jbecirovski'


class sGoBehindTargetGoal_GK(SkillBase):
    """
    Skill which set position between ball and yellow goal inside goal area.
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pst_target, pst_goal):
        dst_target_player = get_distance(pst_goal, pst_target)
        new_pos = Pose(pst_target, get_angle(pst_goal, pst_target))
        new_pos.position = stayInsideCircle(new_pos.position, pst_goal, dst_target_player / 2)
        new_pos.position = stayInsideCircle(new_pos.position, pst_goal, 350)
        new_pos.position = stayInsideSquare(new_pos.position, 300, -300, 2500, 2920)
        return new_pos
