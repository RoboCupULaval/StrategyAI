from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RuleSSL_Python.Util.Pose import Pose

__author__ = 'jbecirovski'


class sFollowTarget(SkillBase):
    """
    sFollowTarget generate next pose which is target pose
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return Pose(pose_target, pose_player.orientation)
