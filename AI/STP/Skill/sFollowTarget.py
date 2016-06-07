# Under MIT License, see LICENSE.txt
""" Action: fait suivre le robot une cible """
from AI.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle

__author__ = 'RoboCupULaval'


class sFollowTarget(SkillBase):
    """ sFollowTarget génère une Pose selon la target """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        angle = get_angle(pose_player.position, pose_target)
        return Pose(pose_target, angle)
