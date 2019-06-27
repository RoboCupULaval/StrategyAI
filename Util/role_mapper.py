from collections import Counter
from typing import Dict

import logging

from Util.role import Role
from ai.GameDomainObjects import Player
from config.config import Config


class NoRoleAvailable(RuntimeError):
    pass


class RoleMapper(object):

    LOCKED_ROLES = []

    # Priority order of assignment for robots with nonfunctional kicker
    BUMPING_ROBOTS_ROLE_ORDER = [
        Role.SECOND_DEFENCE,
        Role.FIRST_DEFENCE,
        Role.MIDDLE,
        Role.SECOND_ATTACK,
        Role.FIRST_ATTACK
    ]

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.roles_translation = {r: None for r in Role.as_list()}

    def clear(self):
        self.roles_translation = {r: None for r in Role.as_list()}

    def map_by_player(self, desired_map: Dict[Role, Player]):
        saved_roles = self._save_locked_roles(self.roles_translation)
        base_map = self._remove_undesired_roles(self.roles_translation, desired_map)

        for key, value in desired_map.items():
            base_map[key] = value

        results = RoleMapper._apply_locked_roles(saved_roles, base_map)

        if abs(len(results.values()) - len(set(results.values()))) > Counter(results.values())[None]:
            raise ValueError("Tried to assign a locked robot to another role, {}".format(Counter(results.values())))
        self.roles_translation = results

    # pylint: disable=invalid-name
    def map_player_to_first_available_role(self, player):
        try:
            role = self.available_roles[0]
            self.roles_translation[role] = player
            return role
        except IndexError:
            raise NoRoleAvailable() from None

    @property
    def available_roles(self):
        return [role for role, player in self.roles_translation.items() if player is None]

    @staticmethod
    def _remove_undesired_roles(base_map, new_map):
        keys = [key for key in base_map.keys()]
        for key in keys:
            if key not in new_map:
                base_map[key] = None
        return base_map

    def _save_locked_roles(self, base_map):
        return {role: base_map[role] for role in self.LOCKED_ROLES}

    @staticmethod
    def _apply_locked_roles(locked_roles_map, result_map):
        for key, value in locked_roles_map.items():
            result_map[key] = value if value is not None else result_map[key]
        return result_map

    def update_player_for_locked_role(self, player, role):
        # This method should NOT be used to swap two robots. We only use it if we
        # explicitely need to update a robot in the LOCKED_ROLES role (ie, referee asks to update goalkeeper)
        assert role in self.LOCKED_ROLES
        old_locked_player = self.roles_translation[role]
        for key, value in self.roles_translation.items():
            if value == player:
                self.roles_translation[key] = old_locked_player
                break
        self.roles_translation[role] = player

    def map_with_rules(self, available_players, required_roles, optional_roles, goalie_id=None):
        nbr_unique_role = len(set(required_roles) | set(optional_roles))
        nbr_role = len(required_roles) + len(optional_roles)
        assert nbr_unique_role == nbr_role, "The same role can not be in the required rules and the optional rules"

        prev_assign = self.roles_translation
        remaining_players = list(available_players.values())

        goal_assign = self._map_goalie_with_ref(remaining_players, required_roles, prev_assign, goalie_id)
        remaining_required_roles = [r for r in required_roles if r not in goal_assign]
        remaining_players = [p for p in remaining_players if p not in goal_assign.values()]

        # Assign robots with nonfunctional kicker
        nonfunctional_kickers_assign = {}
        working_kicker_ids = Config()["COACH"]["working_kicker_ids"]
        remaining_functional_kickers = [p for p in remaining_players if p.id in working_kicker_ids]
        remaining_nonfunctional_kickers = [p for p in remaining_players if p not in remaining_functional_kickers]

        nb_nonfunctional_kickers_to_assign = len(remaining_required_roles) - len(remaining_functional_kickers)
        if nb_nonfunctional_kickers_to_assign > 0:
            for role in self.BUMPING_ROBOTS_ROLE_ORDER:
                if role in remaining_required_roles:
                    nonfunctional_kickers_assign[remaining_nonfunctional_kickers.pop()] = role
                    remaining_required_roles.remove(role)
                    nb_nonfunctional_kickers_to_assign -= 1

        required_assign = self._keep_prev_mapping_otherwise_random(remaining_functional_kickers,
                                                                   remaining_required_roles,
                                                                   prev_assign,
                                                                   is_required_roles=True)

        remaining_functional_kickers = [p for p in remaining_functional_kickers if p not in required_assign.values()]

        nb_nonfunctional_kickers_to_assign = len(optional_roles) - len(remaining_functional_kickers)
        if nb_nonfunctional_kickers_to_assign > 0:
            for role in self.BUMPING_ROBOTS_ROLE_ORDER:
                if role in optional_roles:
                    nonfunctional_kickers_assign[remaining_nonfunctional_kickers.pop()] = role
                    optional_roles.remove(role)
                    nb_nonfunctional_kickers_to_assign -= 1

        optional_assign = self._keep_prev_mapping_otherwise_random(remaining_functional_kickers,
                                                                   optional_roles,
                                                                   prev_assign,
                                                                   is_required_roles=False)

        self.roles_translation = {**goal_assign, **required_assign, **optional_assign, **nonfunctional_kickers_assign}
        return self.roles_translation

    def _keep_prev_mapping_otherwise_random(self, remaining_players, roles, prev_assign, is_required_roles):
        roles_stay_same = {r: prev_assign[r] for r in roles
                           if r in prev_assign and prev_assign[r] in remaining_players}

        remaining_roles = [r for r in roles if r not in roles_stay_same]
        remaining_player = [p for p in remaining_players if p not in roles_stay_same.values()]

        if is_required_roles:
            assert len(remaining_roles) <= len(remaining_player), \
                "Not enough player left ({} players) to assign theses roles {}".format(len(remaining_player),
                                                                                       remaining_roles)
        random_assignment = dict(zip(remaining_roles, remaining_player))
        return {**roles_stay_same, **random_assignment}

    def _map_goalie_with_ref(self, remaining_player, required_roles, prev_assign, goalie_id):
        if Role.GOALKEEPER in required_roles:
            for p in remaining_player:
                if p.id == goalie_id:
                    if Role.GOALKEEPER not in prev_assign or prev_assign[Role.GOALKEEPER].id != goalie_id:
                        self.logger.info("The referee force goalie to be {}".format(p))
                    return {Role.GOALKEEPER: p}
        return {}

