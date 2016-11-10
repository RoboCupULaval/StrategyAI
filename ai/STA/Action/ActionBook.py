# Under MIT License, see LICENSE.txt

from .GoBehind import GoBehind
from .GoBetween import GoBetween
from .GrabBall import GrabBall
from .Idle import Idle
from .Kick import Kick
from .MoveTo import MoveTo
from .MoveWithBall import MoveWithBall
from .ProtectGoal import ProtectGoal


class ActionBook(object):
    def __init__(self):
        self.ActionBook = {'GoBehind': GoBehind,
                           'GoBetween': GoBetween,
                           'GrabBall': GrabBall,
                           'Idle': Idle,
                           'Kick': Kick,
                           'MoveTo': MoveTo,
                           'MoveWithBall': MoveWithBall,
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

