from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle

__author__ = 'jama'


class sFaceTarget(SkillBase):
    """
    sFaceTarget align the player orientation with the target pose
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return Pose(pose_player, get_angle(pose_player, pose_target))
