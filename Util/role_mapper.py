from collections import Counter
from .role import Role


class RoleMapper(object):
    LOCKED_ROLES = [Role.GOALKEEPER]

    def __init__(self):
        self.roles_translation = {r: None for r in Role}

    def map_by_player(self, desired_map):
        saved_roles = self._save_locked_roles(self.roles_translation)
        base_map = self._remove_undesired_roles(self.roles_translation, desired_map)

        for key, value in desired_map.items():
            base_map[key] = value

        results = self._apply_locked_roles(saved_roles, base_map)

        if abs(len(results.values()) - len(set(results.values()))) > Counter(results.values())[None]:
            raise ValueError("Tried to assign a locked robot to another role, {}".format(Counter(results.values())))
        self.roles_translation = results

    def _remove_undesired_roles(self, base_map, new_map):
        keys = [key for key in base_map.keys()]
        for key in keys :
            if key not in new_map :
                base_map[key] = None
        return base_map

    def _save_locked_roles(self, base_map):
        return {role: base_map[role] for role in self.LOCKED_ROLES}

    def _apply_locked_roles(self, locked_roles_map, result_map):
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
