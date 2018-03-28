from collections import Counter

from Util.role import Role


class NoRoleAvailable(RuntimeError):
    pass


class RoleMapper(object):

    LOCKED_ROLES = []

    def __init__(self):
        self.roles_translation = {r: None for r in Role.as_list()}

    def map_by_player(self, desired_map):
        saved_roles = self._save_locked_roles(self.roles_translation)
        base_map = self._remove_undesired_roles(self.roles_translation, desired_map)

        for key, value in desired_map.items():
            base_map[key] = value

        results = RoleMapper._apply_locked_roles(saved_roles, base_map)

        if abs(len(results.values()) - len(set(results.values()))) > Counter(results.values())[None]:
            raise ValueError("Tried to assign a locked robot to another role, {}".format(Counter(results.values())))
        self.roles_translation = results

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
        for key in keys :
            if key not in new_map :
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
