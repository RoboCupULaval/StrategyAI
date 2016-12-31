# Under MIT License, see LICENSE.txt

from .GoBehind import GoBehind
from .GoBetween import GoBetween
from .GetBall import GetBall
from .Idle import Idle
from .Kick import Kick
from .MoveToPosition import MoveToPosition
from .MoveDribblingBall import MoveDribblingBall
from .ProtectGoal import ProtectGoal


class ActionBook(object):
    def __init__(self):
        self.ActionBook = {'GoBehind': GoBehind,
                           'GoBetween': GoBetween,
                           'GrabBall': GetBall,
                           'Idle': Idle,
                           'Kick': Kick,
                           'MoveTo': MoveToPosition,
                           'MoveWithBall': MoveDribblingBall,
                           'ProtectGoal': ProtectGoal}

    def get_actions_name_list(self):
        return list(self.ActionBook.keys())

    def check_existance_action(self, action_name):
        assert isinstance(action_name, str)

        return action_name in self.ActionBook

    def get_action(self, action_name):
        if self.check_existance_action(action_name):
            return self.ActionBook[action_name]
        return self.ActionBook['Idle']

