from abc import abstractmethod

__author__ = 'jbecirovski'

class PlayBase:
    """
    Play contain:
    + Contain Sequence of Tactics for each bots
    + Play book - Regroup all plays in dictionary {'Play.__name__':Play object}
    """
    @abstractmethod
    def __init__(self, name='pBook'):
        self.name = name

    @abstractmethod
    def getTactics(self, index=None):
        """
        :return: list like [[TacticR0, TacticR1, ... , TacticR5],
                            [...                               ]]
        """
        pass

    def __getitem__(self, item):
        """
        :param item: str
        :return: Play
        """
        return self.getBook()[item]

    def getBook(self):
        """
        :return: dict like {'Play.__name__' = Play}
        """
        return dict(zip([cls.__name__ for cls in self.__class__.__subclasses__()], self.__class__.__subclasses__()))