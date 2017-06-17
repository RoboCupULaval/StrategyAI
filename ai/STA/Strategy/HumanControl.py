# Under MIT license, see LICENSE.txt
from ai.Util.role import Role
from ai.states.game_state import GameState
from . Strategy import Strategy
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.Stop import Stop


class HumanControl(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        for r in Role:
            self.add_tactic(r, Stop)
            print(r)
        print("HUMANCONTROL out")

    def assign_tactic(self, tactic: Tactic, robot_id: int):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)

        self.roles_graph[robot_id].remove_node(0)
        self.add_tactic(robot_id, tactic)
