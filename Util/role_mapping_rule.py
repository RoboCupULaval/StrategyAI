from typing import Dict

from Util.role import Role
from ai.GameDomainObjects import Player


class ImpossibleToMap(BaseException):
    pass


def keep_prev_mapping_otherwise_random(available_players, target_role: Role, role_mapping: Dict[Role, Player]) -> Player:
    if role_mapping[target_role] is not None:
        return role_mapping[target_role]
    assigned_players = [player for player in role_mapping.values() if player is not None]

    for player in available_players:
        if player not in assigned_players:
            return player
    raise ImpossibleToMap("No player available for mapping")


