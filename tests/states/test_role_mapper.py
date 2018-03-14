from unittest import TestCase

from Util.role import Role
from ai.states.game_state import GameState


class RoleMapperTests(TestCase):
    def test_map_roles_no_mapping(self):
        state = GameState()
        state.map_players_to_roles_by_player(BASIC_ROLES)
        self.assertDictEqual(state.role_mapping, BASIC_ROLES)

    def test_switch_mapping(self):
        state = GameState()
        state.map_players_to_roles_by_player(BASIC_ROLES)
        state.map_players_to_roles_by_player(INVERTED_ROLES_NO_GOAL)
        self.assertDictEqual(state.role_mapping, INVERTED_ROLES_NO_GOAL)

    def test_remove_unassigned_mappings(self):
        state = GameState()
        state.map_players_to_roles_by_player(BASIC_ROLES)
        state.map_players_to_roles_by_player(MISSING_MIDDLE)
        self.assertDictEqual(state.role_mapping, MISSING_MIDDLE_EXPECTED)

    # def test_givenBasicMapping_whenMapMissingLockedRole_thenKeepsLockedRole(self):
    #     state = GameState()
    #     state.map_players_to_roles_by_player(BASIC_ROLES)
    #     state.map_players_to_roles_by_player(MISSING_REQUIRED)
    #     self.assertDictEqual(state.get_role_mapping(), MISSING_REQUIRED_EXPECTED)

    # def test_givenBasicMapping_whenRemapLockedRole_thenThrowsValueError(self):
    #     state = GameState()
    #     state.map_players_to_roles_by_player(BASIC_ROLES)
    #     with self.assertRaises(ValueError):
    #         state.map_players_to_roles_by_player(INVERTED_ROLES)

    # def test_givenLockedRole_whenUpdateLockedRole_thenSwapsRobots(self):
    #     state = GameState()
    #     state.map_players_to_roles_by_player(BASIC_ROLES)
    #     state.update_id_for_locked_role(1, Role.GOALKEEPER)
    #     self.assertDictEqual(state.get_role_mapping(), GOALKEEPER_SWAPPED)


BASIC_ROLES = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: 3,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

GOALKEEPER_SWAPPED = {
    Role.GOALKEEPER: 1,
    Role.FIRST_DEFENCE: 0,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: 3,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

INVERTED_ROLES = {
    Role.GOALKEEPER: 5,
    Role.FIRST_DEFENCE: 4,
    Role.SECOND_DEFENCE: 3,
    Role.MIDDLE: 2,
    Role.FIRST_ATTACK: 1,
    Role.SECOND_ATTACK: 0
}

INVERTED_ROLES_NO_GOAL = {
    Role.FIRST_DEFENCE: 4,
    Role.SECOND_DEFENCE: 3,
    Role.MIDDLE: 2,
    Role.FIRST_ATTACK: 1,
    Role.SECOND_ATTACK: 5,
    Role.GOALKEEPER: 0
}

MISSING_MIDDLE = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}
MISSING_MIDDLE_EXPECTED = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: None,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

MISSING_REQUIRED = {
    Role.MIDDLE: 3,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 5,
    Role.SECOND_ATTACK: 4
}

MISSING_REQUIRED_EXPECTED = {
    Role.MIDDLE: 3,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 5,
    Role.SECOND_ATTACK: 4,
    Role.GOALKEEPER: 0
}
