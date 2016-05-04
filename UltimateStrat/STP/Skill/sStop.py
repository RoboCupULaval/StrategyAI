from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose, Position

__author__ = 'jbecirovski'


class sStop(SkillBase):
    """
    sStop immobilize bot with current position
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return Pose(pose_player.position, pose_player.orientation)
