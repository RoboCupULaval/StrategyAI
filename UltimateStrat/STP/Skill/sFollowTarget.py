#Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import *

__author__ = 'RoboCupULaval'


class sFollowTarget(SkillBase):
    """
    sFollowTarget generate next pose which is target pose
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        angle = get_angle(pose_player.position, pose_target)
        return Pose(pose_target, angle)
