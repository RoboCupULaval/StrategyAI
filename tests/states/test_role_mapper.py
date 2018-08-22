from unittest import TestCase

import pytest

from Util.role import Role
from Util.role_mapper import RoleMapper
from Util.team_color_service import TeamColorService
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState


class RoleMapperTests(TestCase):

    def setUp(self):
        self.state = GameState()
        self.role_mapper = RoleMapper()

    def test_givenNoMapping_whenMapById_thenMapsAllPlayers(self):
        self.state.map_players_to_roles_by_player(basic_roles)
        self.assertDictEqual(self.state.role_mapping, basic_roles)

    def test_givenBasicMapping_whenMapOtherwise_thenMapsPlayersProperly(self):
        self.state.map_players_to_roles_by_player(basic_roles)
        self.state.map_players_to_roles_by_player(inverted_roles_no_goal)
        self.assertDictEqual(self.state.role_mapping, inverted_roles_no_goal)

    def test_givenBasicMapping_whenMapFewerRobots_thenRemovesUnasignedOnes(self):
        self.state.map_players_to_roles_by_player(basic_roles)
        self.state.map_players_to_roles_by_player(missing_middle)
        self.assertDictEqual(self.state.role_mapping, missing_middle_expected)

    def test_whenMapRuleWithDuplicateRole_thenAssertError(self):
        A_ROLE_RULE = {Role.GOALKEEPER: None}

        with pytest.raises(AssertionError):
            self.role_mapper.map_with_rules([], A_ROLE_RULE, A_ROLE_RULE)

    def test_whenMappingWithMoreOptionalRoleThenPlayers_thenOnlyMapTheNumberOfPlayer(self):
        A_SET_AVAILABLE_PLAYER = {1: Player(1, TeamColorService.BLUE),
                                  2: Player(2, TeamColorService.BLUE)}
        LESS_ROLE_THEN_PLAYER = [Role.GOALKEEPER,
                                 Role.MIDDLE,
                                 Role.SECOND_ATTACK]
        mapping = self.role_mapper.map_with_rules(A_SET_AVAILABLE_PLAYER, {}, LESS_ROLE_THEN_PLAYER)

        assert len(A_SET_AVAILABLE_PLAYER) == len(mapping)

    def test_whenMappingWithMoreRequiredRoleThenPlayers_thenAssert(self):
        A_SET_AVAILABLE_PLAYER = {1: Player(1, TeamColorService.BLUE),
                                  2: Player(2, TeamColorService.BLUE)}
        LESS_ROLE_THEN_PLAYER = [Role.GOALKEEPER,
                                 Role.MIDDLE,
                                 Role.SECOND_ATTACK]
        with self.assertRaises(AssertionError):
            self.role_mapper.map_with_rules(A_SET_AVAILABLE_PLAYER, LESS_ROLE_THEN_PLAYER, {})


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
