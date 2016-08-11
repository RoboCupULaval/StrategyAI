from .GoGetBall import GoGetBall
from .GoalKeeper import GoalKeeper
from .GoToPosition import GoToPosition
from .Stop import Stop
from .CoverZone import CoverZone

TACTIC_BOOK = {'goto_position' : GoToPosition,
               'goalkeeper' : GoalKeeper,
               'cover_zone' : CoverZone,
               'get_ball' : GoGetBall}
