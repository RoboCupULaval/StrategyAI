from typing import List


class PathfinderHistory:
    def __init__(self):
        self.last_path = None
        self.last_raw_path = None
        self.path = None
        self.path_speed = None
        self.last_pose_goal = None

    @property
    def last_path(self):
        return self.last_path

    @last_path.setter
    def last_path(self, value: List):
        assert isinstance(value, list)
        self.last_path = value

    @property
    def last_raw_path(self):
        return self.last_raw_path

    @last_raw_path.setter
    def last_raw_path(self, value: List):
        assert isinstance(value, list)
        self.last_raw_path = value

    @property
    def path(self):
        return self.path

    @path.setter
    def path(self, value: List):
        assert isinstance(value, list)
        self.path = value

    @property
    def path_speed(self):
        return self.path_speed

    @path_speed.setter
    def path_speed(self, value: List):
        assert isinstance(value, list)

    @property
    def last_pose_goal(self):
        return self.last_pose_goal

    @last_pose_goal.setter
    def last_pose_goal(self, value: Pose):
        assert isinstance()