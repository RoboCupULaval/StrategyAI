# Under MIT License, see LICENSE.txt
from ai.STA.Tactic.test_turn_on_you import TestTurnOnYou
from .GoGetBall import GoGetBall
from .GoalKeeper import GoalKeeper
from .GoToPosition import GoToPosition
from .RotateAroundBall import RotateAroundBall
from .Stop import Stop
from .ProtectZone import ProtectZone
from .DemoFollowBall import DemoFollowBall
from .GoToPositionNoPathfinder import GoToPositionNoPathfinder
from .goToPositionPathfinder import GoToPositionPathfinder
from .go_kick import GoKick


class TacticBook(object):
    def __init__(self):
        self.tactic_book = {'GoToPosition': GoToPosition,
                            'GoalKeeper': GoalKeeper,
                            'CoverZone': ProtectZone,
                            'GoGetBall': GoGetBall,
                            'DemoFollowBall': DemoFollowBall,
                            'Stop': Stop,
                            'GoToPositionNoPathfinder': GoToPositionNoPathfinder,
                            'GoToPositionPathfinder': GoToPositionPathfinder,
                            'GoKick': GoKick,
                            "TestTurnOnYou": TestTurnOnYou}

    def get_tactics_name_list(self):
        return list(self.tactic_book.keys())

    def check_existance_tactic(self, tactic_name):
        assert isinstance(tactic_name, str)

        return tactic_name in self.tactic_book

    def get_tactic(self, tactic_name):
        if self.check_existance_tactic(tactic_name):
            return self.tactic_book[tactic_name]
        return self.tactic_book['Stop']

