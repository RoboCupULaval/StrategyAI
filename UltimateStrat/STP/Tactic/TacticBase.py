from abc import abstractmethod

__author__ = 'RoboCupULaval'

class TacticBase:
    """
    Tactic contain:
    + Contain Behavior which select skill according to current situation
    + Tactic book - Regroup all tactical behaviors in dictionary {'Tactical.__name__':Tactic object}
    """
    @abstractmethod
    def __init__(self, name='tBook'):
        self.name = name

    @abstractmethod
    def apply(self, info_manager, id_player):
        """
        Apply to specific bot for a tactical behavior and set next skill.
        :param info_manager: InfoManager object
        :param id_player: int
        :return: dict like ['skill': str, 'target': Position, 'goal': Position]

        """
        pass

    def __getitem__(self, item):
        """
        :param item: str
        :return: Tactical
        """
        return self.getBook()[item]

    def getBook(self):
        """
        :return: dict like {'Tactical.__name__' = Tactical}
        """
        return dict(zip([cls.__name__ for cls in self.__class__.__subclasses__()], self.__class__.__subclasses__()))