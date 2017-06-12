# Under MIT license, see LICENSE.txt
from ai.states.game_state import GameState
from . Strategy import Strategy
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.Stop import Stop


class HumanControl(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        print(self.game_state.my_team.available_players.values())

        for player in self.game_state.my_team.available_players.values():
            print("HEROEHO",player)
            self.add_tactic(player.id, Stop(self.game_state, player))

    def assign_tactic(self, tactic: Tactic, robot_id: int):
        assert isinstance(tactic, Tactic)
        assert isinstance(robot_id, int)

        self.graphs[robot_id].remove_node(0)
        self.add_tactic(robot_id, tactic)
