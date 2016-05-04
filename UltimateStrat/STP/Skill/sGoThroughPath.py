__author__ = 'magal106'

from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import *

class sGoThroughPath(SkillBase):
    """

    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)

    def act(self, pose_player, pose_target, pose_goal):
        return pose_target

