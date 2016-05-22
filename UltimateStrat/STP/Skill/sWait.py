Under MIT License, see LICENSE.txt
from UltimateStrat.STP.Skill.SkillBase import SkillBase

__author__ = 'RoboCupULaval'


class sWait(SkillBase):
    """
    sWait is a no-change action
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return None
