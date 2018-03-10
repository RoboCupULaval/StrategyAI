
from collections import namedtuple

from Util import AICommand
from ai.GameDomainObjects import Player


EngineCommand = namedtuple('EngineCommand',
                           'robot_id,'
                           'cruise_speed,'
                           'path,'
                           'kick_type,'
                           'kick_force,'
                           'dribbler_active,'
                           'charge_kick,'
                           'target_orientation,'
                           'end_speed,')


def generate_engine_cmd(player: Player, ai_cmd: AICommand, path):
    return EngineCommand(player.id,
                         cruise_speed=ai_cmd.cruise_speed * 1000,
                         path=path,
                         kick_type=ai_cmd.kick_type,
                         kick_force=ai_cmd.kick_force,
                         dribbler_active=ai_cmd.dribbler_active,
                         target_orientation=ai_cmd.target.orientation if ai_cmd.target else None,
                         end_speed=ai_cmd.end_speed,
                         charge_kick=ai_cmd.charge_kick)
