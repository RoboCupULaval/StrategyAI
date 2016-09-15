from .GoGetBall import GoGetBall
from .GoalKeeper import GoalKeeper
from .GoToPosition import GoToPosition
from .RotateAround import RotateAround
from .Stop import Stop
from .CoverZone import CoverZone

class TacticBook(object):
    def __init__(self):
        self.tactic_book = {'goto_position' : GoToPosition,
                            'goalkeeper' : GoalKeeper,
                            'cover_zone' : CoverZone,
                            'get_ball' : GoGetBall,
                            "rotate_around": RotateAround}

    def get_tactics_name_list(self):
        return list(self.tactic_book.keys())
