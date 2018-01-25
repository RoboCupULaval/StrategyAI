# Under MIT license, see LICENSE.txt
from Util.role import Role
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class HumanControl(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        for r in Role:
            p = self.game_state.get_player_by_role(r)
            if p is None:
                continue
            self.add_tactic(r, Stop(self.game_state, p))

    def assign_tactic(self, tactic: Tactic, robot_id: int):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)

        r = self.game_state.get_role_by_player_id(robot_id)
        if r is None:
            self.game_state.map_players_to_roles_by_player_id({robot_id: Role.FIRST_ATTACK})  # TODO
            r = Role.FIRST_ATTACK
        else:
            self.roles_graph[r].remove_node(0)
        self.add_tactic(r, tactic)

