from .GoGetBall import GoGetBall
from .GoalKeeper import GoalKeeper
from .GoToPosition import GoToPosition
from .Stop import Stop
from .CoverZone import CoverZone
from .DemoFollowBall import DemoFollowBall


class TacticBook(object):
    def __init__(self):
        self.tactic_book = {'GoToPosition': GoToPosition,
                            'GoalKeeper': GoalKeeper,
                            'CoverZone': CoverZone,
                            'GoGetBall': GoGetBall,
                            'DemoFollowBall': DemoFollowBall,
                            'Stop': Stop}

    def get_tactics_name_list(self):
        return list(self.tactic_book.keys())

    def check_existance_tactic(self, tactic_name):
        assert isinstance(tactic_name, str)

        return tactic_name in self.tactic_book

    def get_tactic(self, tactic_name):
        if self.check_existance_tactic(tactic_name):
            return self.tactic_book[tactic_name]
        return self.tactic_book['Stop']

