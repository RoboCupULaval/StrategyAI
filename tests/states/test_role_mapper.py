from unittest import TestCase
from ai.Util.role import Role
from ai.states.game_state import GameState

class RoleMapperTests(TestCase):
    def test_givenNoMapping_whenMapById_thenMapsAllPlayers(self):
        state = GameState()
        state.map_players_to_roles_by_player(basic_roles)
        self.assertDictEqual(state.get_role_mapping(), basic_roles)

    def test_givenBasicMapping_whenMapOtherwise_thenMapsPlayersProperly(self):
        state = GameState()
        state.map_players_to_roles_by_player(basic_roles)
        state.map_players_to_roles_by_player(inverted_roles_no_goal)
        self.assertDictEqual(state.get_role_mapping(), inverted_roles_no_goal)

    def test_givenBasicMapping_whenMapFewerRobots_thenRemovesUnasignedOnes(self):
        state = GameState()
        state.map_players_to_roles_by_player(basic_roles)
        state.map_players_to_roles_by_player(missing_middle)
        self.assertDictEqual(state.get_role_mapping(), missing_middle_expected)

    def test_givenBasicMapping_whenMapMissingLockedRole_thenKeepsLockedRole(self):
        state = GameState()
        state.map_players_to_roles_by_player(basic_roles)
        state.map_players_to_roles_by_player(missing_required)
        self.assertDictEqual(state.get_role_mapping(), missing_required_expected)

    def test_givenBasicMapping_whenRemapLockedRole_thenThrowsValueError(self):
        state = GameState()
        state.map_players_to_roles_by_player(basic_roles)
        with self.assertRaises(ValueError):
            state.map_players_to_roles_by_player(inverted_roles)

    def test_givenLockedRole_whenUpdateLockedRole_thenSwapsRobots(self):
        state = GameState()
        state.map_players_to_roles_by_player(basic_roles)
        state.update_id_for_locked_role(1, Role.GOALKEEPER)
        self.assertDictEqual(state.get_role_mapping(), goalkeeper_swapped)


basic_roles = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: 3,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

goalkeeper_swapped = {
    Role.GOALKEEPER: 1,
    Role.FIRST_DEFENCE: 0,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: 3,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

inverted_roles = {
    Role.GOALKEEPER: 5,
    Role.FIRST_DEFENCE: 4,
    Role.SECOND_DEFENCE: 3,
    Role.MIDDLE: 2,
    Role.FIRST_ATTACK: 1,
    Role.SECOND_ATTACK: 0
}

inverted_roles_no_goal = {
    Role.FIRST_DEFENCE: 4,
    Role.SECOND_DEFENCE: 3,
    Role.MIDDLE: 2,
    Role.FIRST_ATTACK: 1,
    Role.SECOND_ATTACK: 5,
    Role.GOALKEEPER: 0
}

missing_middle = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}
missing_middle_expected = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: None,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

missing_required = {
    Role.MIDDLE: 3,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 5,
    Role.SECOND_ATTACK: 4
}

missing_required_expected = {
    Role.MIDDLE: 3,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 5,
    Role.SECOND_ATTACK: 4,
    Role.GOALKEEPER: 0
}
