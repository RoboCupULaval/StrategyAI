# Under MIT license, see LICENSE.txt
from Util.role import Role
from Util.role_mapper import NoRoleAvailable
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class HumanControl(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

    def assign_tactic(self, tactic: Tactic, robot_id: int):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)

        role = self.game_state.get_role_by_player_id(robot_id)

        if role is None:
            try:
                role = self.game_state.map_player_to_first_available_role(robot_id)
            except NoRoleAvailable:
                # When all else fail, just force it
                role = Role.FIRST_ATTACK
                self.game_state.map_players_to_roles_by_player_id({role: robot_id})

        self.clear_graph_of_role(role)
        self.create_node(role, tactic)

    @classmethod
    def required_roles(cls):
        return []

