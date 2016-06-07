#Under MIT License, see LICENSE.txt
from ai.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose
import copy

__author__ = 'RoboCupULaval'


class sNull(SkillBase):
    """
    sNull generate next pose which is its pose
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return copy.deepcopy(pose_player)
