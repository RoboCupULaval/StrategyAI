from abc import abstractmethod, ABCMeta

from Util import Pose


class RegulatorBaseClass(metaclass=ABCMeta):

    @abstractmethod
    def execute(self, robot, dt) -> Pose:
        pass

    @abstractmethod
    def reset(self):
        pass
