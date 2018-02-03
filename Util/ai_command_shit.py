from collections import ChainMap
from enum import Enum

from Util.Pose import Pose
from Util.Velocity import Velocity
from ai.GameDomainObjects import Player


class AICommandType(Enum):
    STOP = 0
    MOVE = 1
    MULTI = 2


class AIControlLoopType(Enum):
    OPEN = 0
    SPEED = 1
    POSITION = 2


_locked_keys = ['player', 'robot_id']

_default_keys = {
    'player': None,
    'robot_id': None,
    'command': None,
    'dribbler_on': False,
    'pathfinder_on': False,
    'kick_strength': 0,
    'charge_kick': False,
    'kick': False,
    'pose_goal': None,
    'speed': Velocity(),
    'cruise_speed': 1.0,
    'end_speed': 0.0,
    'collision_ball': False,
    'control_loop_type': AIControlLoopType.POSITION,
    'path': [],
    'path_speeds': [0.0, 0.0],
}

_keys_type = {
    'player': Player,
    'robot_id': (int, float),
    'command': AICommandType,
    'dribbler_on': bool,
    'pathfinder_on': bool,
    'kick_strength': (int, float),
    'charge_kick': bool,
    'kick': bool,
    'pose_goal': Pose,
    'speed': Velocity,
    'cruise_speed': (int, float),
    'end_speed': (int, float),
    'collision_ball': bool,
    'control_loop_type': AIControlLoopType,
    'path': list,
    'path_speeds': list,
}


class AICommand(ChainMap):
    """
    Contains the AI state of a robot before sending it.
    """
    def __init__(self, player: Player, command: AICommandType=AICommandType.STOP, **kwargs):
        kwargs['player'] = player
        kwargs['robot_id'] = player.id
        kwargs['command'] = command
        AICommand._validate_keys_value_type(**kwargs)
        super().__init__(kwargs, _default_keys)

    @staticmethod
    def _validate_keys_value_type(**kwargs):
        for key, value in kwargs.items():
            if not isinstance(value, _keys_type[key]):
                raise TypeError('The value of the key `{}` need to be of the type: {}.\n'.format(key, _keys_type[key])
                                + 'Type received: {}'.format(type(value)))

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setattr__(self, key, value):
        if key in _locked_keys:
            raise KeyError('The key `{}` is immutable.')
        elif key in _default_keys:
            self.__setitem__(key, value)
        else:
            return super().__setattr__(key, value)

    def __missing__(self, key):
        raise KeyError('The following given key does not exist: ' + key)
