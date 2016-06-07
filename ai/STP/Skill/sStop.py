#Under MIT License, see LICENSE.txt
from ai.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose, Position

__author__ = 'RoboCupULaval'


class sStop(SkillBase):
    """
    sStop immobilize bot with current position
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return Pose(pose_player.position, pose_player.orientation)
