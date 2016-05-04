from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle

__author__ = 'Yassine'


class sFaceTarget(SkillBase):
    """
    sFaceTarget align the player orientation with the target pose.
    If the pose_goal is a line (tuple) the player takes the line orientation.
    If the pose_goal is a Position, the player simply face the target
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        if isinstance(pose_goal, tuple):
            # The pose_goal is a tuple (coordinates of a line)
            angle = get_angle(pose_goal[0], pose_goal[1])
        else:
            # The pose_goal is a position
            angle = get_angle(pose_target, pose_goal)
        return Pose(pose_target, angle)
