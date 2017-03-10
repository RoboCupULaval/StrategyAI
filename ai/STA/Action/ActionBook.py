# Under MIT License, see LICENSE.txt
from ai.STA.Action.Move import Move
from ai.STA.Action.RotateArround import RotateAround
from .GoBehind import GoBehind
from .GoBetween import GoBetween
from .GetBall import GetBall
from .Idle import Idle
from .Kick import Kick
from .MoveToPosition import MoveToPosition
from .MoveToDribblingBall import MoveToDribblingBall
from .ProtectGoal import ProtectGoal
from .PathfindToPosition import PathfindToPosition


class ActionBook(object):
    def __init__(self):
        self.ActionBook = {'GoBehind': GoBehind,
                           'GoBetween': GoBetween,
                           'GrabBall': GetBall,
                           'Idle': Idle,
                           'Kick': Kick,
                           'Move': Move,
                           'MoveTo': MoveToPosition,
                           'MoveWithBall': MoveToDribblingBall,
                           'ProtectGoal': ProtectGoal,
                           'PathfindToPosition': PathfindToPosition,
                           'RotateAround': RotateAround}

    def get_actions_name_list(self):
        return list(self.ActionBook.keys())

    def check_existance_action(self, action_name):
        assert isinstance(action_name, str)

        return action_name in self.ActionBook

    def get_action(self, action_name):
        if self.check_existance_action(action_name):
            return self.ActionBook[action_name]
        return self.ActionBook['Idle']

