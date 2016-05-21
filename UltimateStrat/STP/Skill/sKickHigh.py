from UltimateStrat.STP.Skill.SkillBase import SkillBase

__author__ = 'RoboCupULaval'


class sKickHigh(SkillBase):
    """
    sKick generate kick if ball is front of it with maximum speed
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return 8
