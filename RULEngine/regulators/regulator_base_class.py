from abc import abstractmethod, ABCMeta

from RULEngine.robot import Robot
from Util import Pose


class RegulatorBaseClass(metaclass=ABCMeta):

    @abstractmethod
    def execute(self, robot: Robot) -> Pose:
        pass

    @abstractmethod
    def reset(self):
        pass
