from UltimateStrat.STP.Skill.SkillBase import SkillBase

__author__ = 'jama'


class sKickLow(SkillBase):
    """
    sKickLow generate kick if ball is front of it with low speed
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return 2
