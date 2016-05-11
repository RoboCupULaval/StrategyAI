from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose, Position

__author__ = 'jbecirovski'


class sGeneratePath(SkillBase):
    """
    sGeneratePath generate a predefined path
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        bot_angle = pose_player.orientation
        return [Pose(Position(0, 0), bot_angle),
                Pose(Position(0, 3000), bot_angle),
                Pose(Position(3000, 3000), bot_angle),
                Pose(Position(3000, 0), bot_angle),
                Pose(Position(0, 0), bot_angle)
                ]
