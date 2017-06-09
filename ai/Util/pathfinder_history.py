from typing import List

from RULEngine.Util.Pose import Pose


class PathfinderHistory:
    def __init__(self):
        self.last_path = None
        self.last_raw_path = None
        self.path = None
        self.path_speed = None
        self.last_pose_goal = None
