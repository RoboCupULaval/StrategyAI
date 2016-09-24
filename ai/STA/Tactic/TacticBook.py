from .GoGetBall import GoGetBall
from .GoalKeeper import GoalKeeper
from .GoToPosition import GoToPosition
from .Stop import Stop
from .CoverZone import CoverZone
from .DemoFollowBall import DemoFollowBall

class TacticBook(object):
    def __init__(self):
        self.tactic_book = {'goto_position' : GoToPosition,
                            'goalkeeper' : GoalKeeper,
                            'cover_zone' : CoverZone,
                            'get_ball' : GoGetBall,
                            'demo_follow_ball' : DemoFollowBall}

    def get_tactics_name_list(self):
        return list(self.tactic_book.keys())
