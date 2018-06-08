from abc import abstractmethod, ABCMeta

from Engine.robot import Robot
from Util import Pose


class RegulatorBaseClass(metaclass=ABCMeta):

    @abstractmethod
    def execute(self, robot) -> Pose:
        pass

    @abstractmethod
    def reset(self):
        pass
