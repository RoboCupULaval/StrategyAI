from abc import abstractmethod

__author__ = 'jbecirovski'


class SkillBase:
    """
    Skill contain :
    + Analyze current situation on the field and generate next specific robot position thanks to its target and goal.
    + Skill book - Regroup all skill action in dictionary {'Skill.__name__':Skill object}
    """
    @abstractmethod
    def __init__(self, name='sBook'):
        self.name = name

    @abstractmethod
    def act(self, target, goal):
        """
        Active skill and set next specific robot position
        :param target: Position
        :param target: Position
        :return: Position
        """
        pass

    def __getitem__(self, item):
        """
        :param item: str
        :return: Skill
        """
        return self.getBook()[item]

    def getBook(self):
        """
        :return: dict like {'Skill.__name__' = Skill}
        """
        return dict(zip([cls.__name__ for cls in self.__class__.__subclasses__()], self.__class__.__subclasses__()))