from UltimateStrat.STP.Skill.SkillBase import SkillBase

__author__ = 'jbecirovski'


class sFollowTarget(SkillBase):
    """
    sFollowTarget generate next pose which is target pose
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, target, goal):
        return target
